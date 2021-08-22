




 Issues
=======

First Attempt Fails
-------------------

After a long rest (may hours) the first attempt to play episodes does not work.
It turns ont he chromecast, but the video is backgrounded.  I think this is a
function of the New Google TV OS.  

If i kill and reset, it corrects itself.  

I might need to start and app, kill it, and then start the episode to fix this?
Maybe if the active app is the background screen, i'll run that sequence.
otherwise ill start the app directly?



Feature Requests
================

Subtitles
---------

Enalbe Subtitles.  Not sure how to embed subtitles in MP4s

"Two More" Button
------------------

When pressed, the last show plays 2 more episodes. Instead of selecting 2
random episodes, it will play the next 2 episodes in sequence from the last set
of shows.

PWA
---

Add the metadata so that this app acts like a progressive web app. 

Select Chromecast from UI
-------------------------

Current, the target chromecast is hardcoded to the bedroom.  It would be nice
if there was a drop-down that let you change the chromecast target on demand

THis will require bidirectioanl communication from the Chromecast controller to
the webapp which shoudl be doable wint a 2nd queue.


Full User Reset
----------------------

The Connection Reset button currently just re-establishes a chromecast
connection.  We shoudl take this a setp further and fully reset the worker by
raising an exception.

Separate Process for Chromecast Manager
---------------------------------------

Instead of running the chromecast controller in a sepraate thread, it might be
cleaner to run it in a separate process.  Then we wont start a new controller
every time Flask spawns a new worker.  

We can use python's multiprocess library's 'Listener' and 'Client' functions to
pass arbitrary python objects to eachother. It will also be easier to test and
validate the controller in isolation

