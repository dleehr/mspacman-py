# Notes

Just dev notes as I build this up - things to think about when going back to asm.

## 2023-01-16

Already surpassed what I have in 65816 version. Have the level map drawn as a background, and then the player sprite on top of that. It's a lot easier to work and refactor in Python as I'm learning how this should work.

I greatly improved the wall detection. One thing I'm not even sure is necessary is the checking alignment for off-axis movement, but it's a fast check.

 Now have dot-eating working. It changes the underlying wall tile index to 0 (just black) and prints a point value to the console. I need to update the score there and draw the score.

 But now what I'm thinking about is how to animate the 4 blinking dots. I could either replace the tile with a different one with the same score, or I could cycle the palette color for that. I bet that back in the day they cycled the palette color.

 Another thought - storing score characters. I didn't do these in the SNES version yet. But they'll definitely be loaded as tile maps. Maybe this just goes as more stuff in `walls.chr`.
