# Streamserver

This is a video stream server , transports live raw h.264 stream data or static h.264 file data to the client. 

This server implements on python [Twisted](www.twistedmatrix.com) framework, supports concurrent input streams.

##Installation

This project is compatible with python 2.6 and twisted 10.1.0

Install from a source code checkout:
    git clone https://github.com/demonyangyue/streamserver.git
  

#Useage

To start the server:
    
    cd ./server
    python coreserver.py
  
This server can be used in two modes:
*live stream server mode, which accepts the raw h.264 stream data as input, you can send the data to the live stream listening port(1557 as default),
and watch the video by vlc player:
    
    vlc rtsp://localhost:1556/stream_1.264
*file stream server mode, which serves the h.264 stream files under the "media" folder. 
    vlc rtsp://localhost:1556/test.264

#Test

The tests are under the "test" folder, based on twisted trial framework, to run them:
    
    nosetests
or

    trial ./test/*.py
