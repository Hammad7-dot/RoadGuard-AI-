"""
RoadGuard AI
Fine-tune YOLOv8 on a real pothole/crack dataset
--------------------------------------------------

The stock ai/models/yolov8n.pt is pretrained on COCO (people, cars,
dogs, etc.) - it has no concept of "pothole" or "crack". To actually
detect road damage, you need to fine-tune on a road-damage dataset.

RECOMMENDED DATASETS (pick one, or merge a couple with Roboflow):

1. RDD2022 / RDD2020 (Road Damage Dataset)
   https://github.com/sekilab/RoadDamageDetector
   Classes: longitudinal crack, transverse crack, alligator crack,
   pothole. Multi-country (Japan, India, Czech, etc.), ~47k images.

2. Pothole Detection Dataset (Roboflow Universe)
   https://universe.roboflow.com/  -> search "pothole detection"
   Several community datasets already in YOLO format, ready to
   download with `roboflow` pip package or a direct zip export.

3. Crack Detection datasets (for segmentation-quality crack masks)
   - CrackForest: https://github.com/cuilimeng/CrackForest-dataset
   - Crack500 / DeepCrack (search on Roboflow/Kaggle)
   Good if you want pixel-level crack masks instead of boxes -
   pair with YOLOv8-seg (`yolov8n-seg.pt`) instead of plain detect.

Any of these downloads (or a Roboflow export) will give you a folder
structured like:

    dataset/
      train/images, train/labels
      valid/images, valid/labels
      test/images,  test/labels
      data.yaml

`data.yaml` looks like:

    train: dataset/train/images
    val: dataset/valid/images
    test: dataset/test/images
    nc: 4
    names: ['pothole', 'longitudinal_crack', 'transverse_crack', 'alligator_crack']

USAGE
-----
    pip install ultralytics roboflow

    # Option A: download a Roboflow dataset directly
    python training/train_road_damage.py --download-roboflow \
        --rf-api-key YOUR_KEY --rf-workspace WORKSPACE --rf-project PROJECT --rf-version 1

    # Option B: you already have a dataset/data.yaml on disk
    python training/train_road_damage.py --data dataset/data.yaml

The trained weights land in runs/detect/train/weights/best.pt.
Copy that over ai/models/yolov8n.pt (or update MODEL_PATH in
utils/constants.py) to plug it straight into the RoadGuard app -
predict(), track(), and the live WebRTC processor all just call
load_model(), so no other code changes are needed.
"""

import argparse
from pathlib import Path

from ultralytics import YOLO


def download_roboflow_dataset(api_key: str, workspace: str, project: str, version: int) -> str:
    from roboflow import Roboflow

    rf = Roboflow(api_key=api_key)
    ds = rf.workspace(workspace).project(project).version(version).download("yolov8")
    return str(Path(ds.location) / "data.yaml")


def train(
    data_yaml: str,
    base_model: str = "yolov8n.pt",
    epochs: int = 100,
    imgsz: int = 640,
    batch: int = 16,
    device: str = "0",
):
    """
    Fine-tune a YOLOv8 model on a road-damage dataset.

    base_model:
        - "yolov8n.pt" for a small/fast model (good default, matches
          the model already shipped in ai/models/)
        - "yolov8s.pt" / "yolov8m.pt" for higher accuracy at the cost
          of speed, if you're not running this on a low-power device
        - "yolov8n-seg.pt" if you downloaded a segmentation-labeled
          crack dataset and want pixel masks instead of boxes
    device:
        "0" for first GPU, "cpu" if no GPU is available (much slower)
    """

    model = YOLO(base_model)

    model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        patience=20,          # early stop if val loss plateaus
        project="runs/detect",
        name="road_damage",
        pretrained=True,
        # Augmentations that help with real-world road footage:
        # variable lighting, motion blur, camera angle.
        degrees=5.0,
        translate=0.1,
        scale=0.3,
        fliplr=0.5,
        mosaic=1.0,
    )

    metrics = model.val()
    print("Validation results:", metrics.results_dict)

    best_weights = Path("runs/detect/road_damage/weights/best.pt")
    print(f"\nBest weights saved to: {best_weights}")
    print("Copy this file to ai/models/ and update MODEL_PATH in "
          "utils/constants.py to use it in the app, e.g.:")
    print('    MODEL_PATH = "ai/models/road_damage_best.pt"')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=str, default=None,
                         help="Path to an existing dataset's data.yaml")
    parser.add_argument("--base-model", type=str, default="yolov8n.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", type=str, default="0")

    parser.add_argument("--download-roboflow", action="store_true",
                         help="Download a dataset from Roboflow Universe first")
    parser.add_argument("--rf-api-key", type=str)
    parser.add_argument("--rf-workspace", type=str)
    parser.add_argument("--rf-project", type=str)
    parser.add_argument("--rf-version", type=int, default=1)

    args = parser.parse_args()

    data_yaml = args.data

    if args.download_roboflow:
        assert args.rf_api_key and args.rf_workspace and args.rf_project, (
            "Provide --rf-api-key, --rf-workspace, and --rf-project "
            "when using --download-roboflow"
        )
        data_yaml = download_roboflow_dataset(
            args.rf_api_key, args.rf_workspace, args.rf_project, args.rf_version
        )

    if not data_yaml:
        raise SystemExit(
            "Provide --data path/to/data.yaml, or use --download-roboflow "
            "with --rf-api-key/--rf-workspace/--rf-project."
        )

    train(
        data_yaml=data_yaml,
        base_model=args.base_model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
    )
