CUDA_VISIBLE_DEVICES=0 python multiview_video_alignment.py --model resnet18 --data can_mh --port 64754 --num_episodes 10 --train_views 4 --note views04- 50 2>&1 | tee ./can_mh-resnet.out
CUDA_VISIBLE_DEVICES=1 python multiview_video_alignment.py --model resnet18 --data lift_mh --port 64755 --num_episodes 10 --train_views 4 --note views04- 2>&1 | tee ./lift_mh-resnet.out
