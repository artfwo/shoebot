#from __future__ import division
import sys, os
import gtk
import cairo
import cairocffi
from socket_server import SocketServerMixin

from shoebot.core import DrawQueueSink


def _UNSAFE_pycairo_context_to_cairocffi(pycairo_context, incref=True):
    # Sanity check. Continuing with another type would probably segfault.
    if not isinstance(pycairo_context, cairo.Context):
        raise TypeError('Expected a cairo.Context, got %r' % pycairo_context)

    # On CPython, id() gives the memory address of a Python object.
    # pycairo implements Context as a C struct:
    #     typedef struct {
    #         PyObject_HEAD
    #         cairo_t *ctx;
    #         PyObject *base;
    #     } PycairoContext;
    # Still on CPython, object.__basicsize__ is the size of PyObject_HEAD,
    # ie. the offset to the ctx field.
    # ffi.cast() converts the integer address to a cairo_t** pointer.
    # [0] dereferences that pointer, ie. read the ctx field.
    # The result is a cairo_t* pointer that cairocffi can use.
    return cairocffi.Context._from_pointer(
        cairocffi.ffi.cast('cairo_t **',
                           id(pycairo_context) + object.__basicsize__)[0],
        incref=True)


ICON_FILE = os.path.join(sys.prefix, 'share', 'pixmaps', 'shoebot-ide.png')

class ShoebotWidget(gtk.DrawingArea, DrawQueueSink, SocketServerMixin):
    '''
    Create a double buffered GTK+ widget on which we will draw using Cairo        
    '''

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    def __init__(self, scale_fit = True):
        gtk.DrawingArea.__init__(self)
        DrawQueueSink.__init__(self)

        self.scale_fit = scale_fit

        # Default picture is the shoebot icon
        if os.path.isfile(ICON_FILE):
            self.backing_store = cairocffi.ImageSurface.create_from_png(ICON_FILE)
        else:
            self.backing_store = cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, 400, 400)
        self.size = None
        self.first_run = True
        self.last_rendering = None

    def do_expose_event(self, event):
        '''
        Draw just the exposed part of the backing store
        '''
        # Create the cairo context
        cr = _UNSAFE_pycairo_context_to_cairocffi(self.window.cairo_create())
        if self.scale_fit:
            source_width = self.backing_store.get_width()
            source_height = self.backing_store.get_height()

            size = self.get_allocation()

            if size.width > source_width or size.height > source_height:
                # Scale up by largest dimension
                if size.width > source_width:
                    xscale = float(size.width) / float(source_width)
                else:
                    xscale = 1.0

                if size.height > source_height:
                    yscale = float(size.height) / float(source_height)
                else:
                    yscale = 1.0

                if xscale > yscale:
                    cr.scale(xscale, xscale)
                else:
                    cr.scale(yscale, yscale)


        cr.set_source_surface(self.backing_store)
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        if self.first_run:
            cr.set_operator(cairocffi.OPERATOR_OVER)
        else:
            cr.set_operator(cairocffi.OPERATOR_SOURCE)
        cr.fill()

    def create_rcontext(self, size, frame):
        '''
        Creates a meta surface for the bot to draw on

        Uses a proxy to an SVGSurface to render on so 
        it's scalable
        '''
        if self.window and not self.size:
            self.set_size_request(*size)
            self.size = size
            while gtk.events_pending():
                gtk.main_iteration_do(block=False)
        extents = (0, 0, size[0], size[1])
        meta_surface = cairocffi.RecordingSurface(cairocffi.CONTENT_COLOR_ALPHA, extents)
        return cairocffi.Context(meta_surface)

    def rendering_finished(self, size, frame, cairo_ctx):
        '''
        Update the backing store from a cairo context and
        schedule a redraw (expose event)
        '''
        if (self.backing_store.get_width(), self.backing_store.get_height()) == size:
            backing_store = self.backing_store
        else:
            backing_store = cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, *size)
        
        cr = cairocffi.Context(backing_store)
        cr.set_source_surface(cairo_ctx.get_target())
        cr.set_operator(cairocffi.OPERATOR_SOURCE)
        cr.paint()
        
        self.backing_store = backing_store
        self.queue_draw()
        
        while gtk.events_pending():
            gtk.main_iteration_do(block=False)

