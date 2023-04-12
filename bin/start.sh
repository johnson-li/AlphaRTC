cd /home/lix16/Workspace/Pandia/AlphaRTC
rm results/* 2> /dev/null

# gn gen out/Default --args='is_debug=true'
ninja -C out/Default peerconnection_serverless && \
tmux send-key -t alpha:0 'LD_LIBRARY_PATH=`pwd`/lib:$LD_LIBRARY_PATH ./peerconnection_serverless ./receiver.json' Enter && \
sleep 1 && \
tmux send-key -t alpha:1 'LD_LIBRARY_PATH=`pwd`/lib:$LD_LIBRARY_PATH ./peerconnection_serverless ./sender2.json' Enter

cd -
