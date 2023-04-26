CUDA_VISIBLE_DEVICES=0 python multiview_video_alignment.py --model deit_tiny_distilled_patch16_224 --data can_mh --port 64754 --num_episodes 10 --train_views 4 --note views04- 50 2>&1 | tee ./can_mh-deit_tiny_distilled.out
CUDA_VISIBLE_DEVICES=1 python multiview_video_alignment.py --model swin_tiny_patch4_window7_224 --data can_mh --port 64755 --num_episodes 10 --train_views 4  --note views04- 2>&1 | tee ./can_mh-swin_tiny.out

CUDA_VISIBLE_DEVICES=2 python multiview_video_alignment.py --model deit_tiny_distilled_patch16_224 --data lift_mh --port 64756 --num_episodes 10 --train_views 4 --note views04- 2>&1 | tee ./lift_mh-deit_tiny_distilled.out
CUDA_VISIBLE_DEVICES=3 python multiview_video_alignment.py --model swin_tiny_patch4_window7_224 --data lift_mh --port 64757 --num_episodes 10 --train_views 4 --note views04- 2>&1 | tee ./lift_mh-swin_tiny.out
