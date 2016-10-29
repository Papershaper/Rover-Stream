# Rover-Stream
Part of my Robot Army development - this project is to manage the streaming of data to-from the rover.

Why??  because I want the primary 'output' of the rover to be a Live Stream and visible to anyone that wants to watch what the rover is doing.  This will allow for a broader audience to follow along the rover's journey.
Also part of Why? the goal is to provide a very simiple interface to the Rover.  This would allow any potential viewer to suggest commands to the rover via the 'live Chat' feature of the streaming service.

The current version is capable of:
1) Generating a liveStream from the rover:  PiCamera -> ffmpeg -> youTube
2) server code can find the active liveBroadcast, and liveChatID.  and read the Chat messages
