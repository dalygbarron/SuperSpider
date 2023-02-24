# Super Spider
Ok got a little problem with the whole event listener thingy. How do you stop
there from being a million of the same event in a row, when you could just
trigger the event once at the end of that process?

Maybe when you call trigger instead of triggering right away it buffers it and
waits for some kind of idle indication, thus if you try to put two of the same
thing in the buffer it skips.

Yeah that is bigly smart.