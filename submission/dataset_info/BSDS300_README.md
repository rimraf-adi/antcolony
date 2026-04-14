# BSDS300 Dataset

**Berkeley Segmentation Dataset and Benchmark (BSDS300)**

- **Source:** https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/bsds/
- **Total Images:** 300 natural images
- **Train/Test Split:** 200 training + 100 test
- **Annotations:** 5-7 independent human segmentations per image
- **Format:** JPEG images (481 x 321 px) + `.seg` annotation files

## Directory Structure Used

```
images/          # 300 grayscale JPEG images (extracted from BSDS300/images/)
human/
  gray/
    *.seg        # Human segmentation annotations
```

## How to Obtain

1. Download from: https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/bsds/BSDS300-images.tgz
2. Extract into the project root
3. Copy images to `images/` and annotations to `human/`

## Citation

Martin, D., Fowlkes, C., Tal, D., & Malik, J. (2001).
"A Database of Human Segmented Natural Images and its Application to
Evaluating Segmentation Algorithms and Measuring Ecological Statistics."
Proc. 8th International Conference on Computer Vision (ICCV), Vol. 2, pp. 416-423.
