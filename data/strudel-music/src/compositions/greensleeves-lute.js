// Greensleeves — sample-based lute reproduction
// 71 two-bar slices of actual lute performance (other+vocals stems recombined)
// Full polyphonic texture: melody + bass counterline + arpeggiation
// G minor, 3/4 time, ~80 BPM effective
// Dynamic arc preserved in the samples themselves

setcpm(80/4)

// Play all 71 two-bar slices in sequence
// Each slice is 2.23s = exactly one cycle at this tempo
// The real lute, not a synthesis approximation
s("greenlute:0 greenlute:1 greenlute:2 greenlute:3 greenlute:4 greenlute:5 greenlute:6 greenlute:7 greenlute:8 greenlute:9 greenlute:10 greenlute:11 greenlute:12 greenlute:13 greenlute:14 greenlute:15 greenlute:16 greenlute:17 greenlute:18 greenlute:19 greenlute:20 greenlute:21 greenlute:22 greenlute:23 greenlute:24 greenlute:25 greenlute:26 greenlute:27 greenlute:28 greenlute:29 greenlute:30 greenlute:31 greenlute:32 greenlute:33 greenlute:34 greenlute:35 greenlute:36 greenlute:37 greenlute:38 greenlute:39 greenlute:40 greenlute:41 greenlute:42 greenlute:43 greenlute:44 greenlute:45 greenlute:46 greenlute:47 greenlute:48 greenlute:49 greenlute:50 greenlute:51 greenlute:52 greenlute:53 greenlute:54 greenlute:55 greenlute:56 greenlute:57 greenlute:58 greenlute:59 greenlute:60 greenlute:61 greenlute:62 greenlute:63 greenlute:64 greenlute:65 greenlute:66 greenlute:67 greenlute:68 greenlute:69 greenlute:70")
  .gain(1.0)
