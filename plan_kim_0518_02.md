# Plan — Baseline U-Net → Enhanced U-Net 단계적 비교

> 작성일: 2026-05-18 (발표 직후)
> 기반 문서: [plan_kim_0518_01.md](plan_kim_0518_01.md), [research_unet.md](research_unet.md)
> 핵심 아이디어: **Baseline 먼저 → 결과 보고 → 강화 → 비교**. 반복적 개선 (Iterative).
> 발표일: 2026-06-15 (약 4주 남음)
> ⚠️ 이 plan은 **검토 전 v0.1**. 구현 시작은 사용자 메모/주석 → v0.2 → 최종 승인 후.

---

## 0. 전략 — 왜 이 순서인가

**원칙**: 강화부터 들어가면 baseline 대비 효과를 모름. **Baseline 결과를 먼저 확정**해야 강화의 의미가 정량적으로 드러남.

```
[현재 가지고 있는 것]
✅ Week 2 PoC (1 epoch, 5K subset) — 동작 확인 끝
✅ data.py / train.py / unet.py / losses.py 등 모듈

[부족한 것]
❌ Baseline 본 학습 결과 (10 epoch on 24K)
❌ 강화 효과의 정량 비교

[목표]
Phase 1 → Baseline 본 학습 결과 확보 (mIoU 0.79 예상)
Phase 2-3 → LM-guided 강화 환경 + 학습 (mIoU 0.83 예상)
Phase 4 → 비교 분석 → Week 3 후반 추가 강화 결정
```

---

## 1. 4단계 Phase 구성

### Phase 1 — Baseline U-Net 본 학습 ✅ **완료 (2026-05-18)**

| 항목 | 결과 |
|------|------|
| 모델 | U-Net (ResNet-34 + ImageNet) |
| 데이터 | CelebAMask-HQ Train 24K |
| Epochs | 20 (실제 best는 epoch 6~7) |
| **Best Val mIoU** | **0.680** ⭐ |
| Final Val mIoU | 0.657 (overfitting) |
| Final Train Loss | 0.17 |
| 진단 | epoch 7 이후 과적합 — Best checkpoint 사용 권장 |

**얻은 인사이트**:
- mIoU 0.68은 face parsing baseline으로 양호
- **Early Stopping 필요** (Phase 3에 반영)
- Augmentation 강화 여지 있음
- 비교 기준선 확정: **0.680**

### Phase 2 — LM-guided 환경 구축 (1~2일)
**목표**: 코드 변경. 학습 X.

**작업 목록**:
1. **`landmark_heatmap.py` 작성** (새 파일, ~100줄)
   - MediaPipe 478점 → (256, 256, 1) Gaussian heatmap
   - 19 클래스로 그룹화 (선택)
2. **`data.py` 수정**
   - `__getitem__`에서 mask와 페어링되는 image의 landmark도 함께 로드
   - 4채널 입력 반환 (RGB + heatmap)
3. **`unet.py` 수정**
   - `build_model(arch, in_channels=4)` 인자 추가
   - smp.Unet의 in_channels=4
4. **`config.yaml` 확장**
   - `model.in_channels: 4` 추가
   - `model.use_landmark: true/false` 토글
5. **단위 테스트**
   - heatmap 생성 검증
   - 4채널 입력 shape 검증

**산출물**:
- `project/segmentation/landmark_heatmap.py` (신규)
- 수정된 `data.py`, `unet.py`, `config.yaml`
- `test_landmark_heatmap.py` (단위 테스트)
- 학습 가능 상태 (실제 학습은 Phase 3에서)

### Phase 3 — LM-guided U-Net 학습 (1일)
**목표**: Phase 1과 같은 조건에서 LM-guided 모델 학습.

| 항목 | Phase 1과 차이 |
|------|--------------|
| 입력 채널 | 3 → **4 (RGB + heatmap)** |
| 첫 conv layer | ResNet-34 stem만 우리가 fine-tune |
| 나머지 | **동일** (data, epochs, loss, aug) |

**중요**: 다른 변수 모두 고정 → **공정한 비교** 가능.

**산출물**:
- `unet_lm.pt` (~85MB)
- Test mIoU, Dice 등
- 시각화 10장

### Phase 4 — 비교 분석 + 의사결정 (1일)
**목표**: 정량 + 정성 비교 → 다음 단계 결정.

**비교 표**:
```
┌─────────────────────────┬──────────┬──────────┬────────┐
│ Model                   │ Baseline │ LM-guided│ Δ      │
├─────────────────────────┼──────────┼──────────┼────────┤
│ Overall Val mIoU        │  0.680   │   ???    │  +???  │
│ Nose IoU                │   ???    │   ???    │  +???  │
│ Eye IoU                 │   ???    │   ???    │  +???  │
│ Mouth IoU               │   ???    │   ???    │  +???  │
│ Skin IoU                │   ???    │   ???    │  +???  │
│ Test Dice               │   ???    │   ???    │  +???  │
│ Occlusion 처리 (정성)   │   60%    │   85%?   │ +25%p  │
│ 학습 시간               │   50분   │   55분   │ +10%   │
└─────────────────────────┴──────────┴──────────┴────────┘
```

**의사결정 분기**:

| LM-guided 결과 | 다음 단계 |
|---------------|----------|
| **큰 향상** (+3%p 이상) | LM-guided 채택 + Week 3 후반 추가 강화 (Attention/Boundary Loss) |
| **소폭 향상** (+1~3%p) | LM-guided 채택, 다른 강화 신중히 |
| **변화 없음** (~0) | Baseline 유지, 다른 방향 시도 (architecture 비교, GAN 강화 등) |
| **악화** | 구현 버그 검토, 또는 그대로 baseline 사용 |

---

## 2. 일정 (5/19 ~ 5/26, 1주)

| 날짜 | Phase | 작업 | 시간 |
|------|-------|------|------|
| **5/19 (월)** | 1 | Baseline 본 학습 (24K, 10 epoch) | 1.5시간 |
| 5/19 | 1 | Test 평가 + 시각화 + 결과 정리 | 2시간 |
| **5/20 (화)** | 2 | landmark_heatmap.py 작성 + 테스트 | 4시간 |
| 5/20 | 2 | data.py / unet.py 수정 | 2시간 |
| **5/21 (수)** | 2 | 단위 테스트 + 1 epoch sanity check | 2시간 |
| 5/21 | 3 | LM-guided 본 학습 (24K, 10 epoch) | 1.5시간 |
| **5/22 (목)** | 3 | Test 평가 + 시각화 | 2시간 |
| 5/22 | 4 | 비교 분석 + 의사결정 회의 | 2시간 |
| **5/23~26** | — | (Phase 4 결정에 따라) 추가 강화 또는 Week 4 준비 | — |

→ **6일 안에 baseline + LM-guided 둘 다 끝**.

---

## 3. 코드 변경 상세 (Phase 2)

### 3.1 신규 파일: `landmark_heatmap.py`

```python
"""MediaPipe 478점 → (256, 256, 1) Gaussian heatmap.

각 랜드마크 위치에 Gaussian (σ=3) 점을 찍고 max 합성.
얼굴 부위 정보를 U-Net 입력에 추가 채널로 제공.
"""
import numpy as np

def create_landmark_heatmap(
    landmarks: np.ndarray,  # (478, 2) int
    size: int = 256,
    sigma: float = 3.0,
) -> np.ndarray:
    """
    Returns: (size, size, 1) float32 in [0, 1]
    """
    H = W = size
    yy, xx = np.mgrid[0:H, 0:W]
    heatmap = np.zeros((H, W), dtype=np.float32)
    for x, y in landmarks:
        if 0 <= x < W and 0 <= y < H:
            g = np.exp(-((xx - x)**2 + (yy - y)**2) / (2 * sigma**2))
            heatmap = np.maximum(heatmap, g)
    return heatmap[..., None]  # (H, W, 1)
```

### 3.2 `data.py` 수정 (Phase 2)

```python
class CelebAMaskHQDataset(Dataset):
    def __init__(self, ..., use_landmark: bool = False):
        ...
        self.use_landmark = use_landmark
        if use_landmark:
            # 사전 계산된 랜드마크 캐시 로드 (또는 inference 시 계산)
            self.landmarks_cache = ...

    def __getitem__(self, idx):
        image = ...  # 기존 코드
        mask = ...

        if self.use_landmark:
            landmarks = self.landmarks_cache[idx]  # (478, 2)
            heatmap = create_landmark_heatmap(landmarks, size=self.input_size)
            # 4채널 concat
            image = np.concatenate([image, heatmap], axis=-1)
        ...
```

> 💡 **랜드마크 사전 계산**: 학습 시 매번 MediaPipe 호출하면 느림. 24K 이미지의 랜드마크를 사전 계산해 `landmarks_cache.npy` 로 저장.

### 3.3 `unet.py` 수정 (Phase 2)

```python
def build_model(
    arch: str = "unet",
    num_classes: int = 6,
    encoder_name: str = "resnet34",
    encoder_weights: str = "imagenet",
    in_channels: int = 3,           # ★ 새 인자
) -> nn.Module:
    arch_map = {"unet": smp.Unet, "unet++": smp.UnetPlusPlus, ...}
    return arch_map[arch.lower()](
        encoder_name=encoder_name,
        encoder_weights=encoder_weights,
        in_channels=in_channels,    # ★ 4 가능
        classes=num_classes,
    )
```

### 3.4 `config.yaml` 확장

```yaml
model:
  arch: unet
  encoder_name: resnet34
  encoder_weights: imagenet
  in_channels: 3                   # ★ baseline=3, lm-guided=4
  use_landmark: false              # ★ true 시 heatmap 추가
```

---

## 4. 비교 시 측정할 것 (Phase 4)

### 4.1 정량 지표
- **mIoU** (메인) — 배경 제외 평균
- **Dice** — F1 유사
- **Per-class IoU** — 어느 부위에서 차이 큰가
- **Confusion Matrix** — 오분류 패턴 차이

### 4.2 정성 지표 (시각화 5장)
- 같은 입력 이미지에 대해 Baseline / LM-guided 예측 나란히
- 특히 **occlusion 케이스** (선글라스, 안경, 측면) 비교

### 4.3 효율 지표
- 학습 시간
- 추론 시간 (1장당)
- 파라미터 수

---

## 5. 가능한 시나리오 + 대응

### 시나리오 A: **LM-guided가 명확히 우수** (+3%p 이상) ★ 가장 가능성 높음
- 채택: LM-guided 사용
- **다음 단계**: Attention Gate 또는 Boundary Loss 추가 (Week 3 후반)

### 시나리오 B: **소폭 향상** (+1~3%p)
- 채택은 하되 신중
- 다음 단계: Attention 같은 추가 강화보다는 **Refinement Network (GAN 후처리)** 강화로 방향 전환

### 시나리오 C: **변화 없음** (~0%p)
- Baseline 유지
- 강화 다른 방향: Architecture 비교 (LinkNet, U-Net++) 또는 GAN 후처리

### 시나리오 D: **악화** (-X%p)
- 구현 버그 검토 (heatmap 정규화, 채널 순서)
- Sanity check: heatmap 시각화 → 입력이 제대로 만들어졌는지 확인
- 1 epoch 만으로 단기 검증

---

## 6. 리스크 + 대응

| 리스크 | 가능성 | 대응 |
|--------|--------|------|
| 24K 학습 시 OOM | LOW | batch_size 16→8 |
| 랜드마크 사전 계산 1시간 이상 | MED | tqdm 진행 표시, GPU 사용 |
| LM-guided 학습이 불안정 | LOW | lr 1e-4 → 5e-5 낮춤 |
| 시간 부족 (5/22까지 못 끝) | MED | LM-guided 5K subset로 짧게 |

---

## 7. Phase별 체크리스트

### Phase 1
- [ ] config: subset_size=null, epochs=10
- [ ] 학습 시작 (T4 GPU 활성화 확인)
- [ ] 학습 완료 (50분)
- [ ] Test mIoU 측정
- [ ] 예측 시각화 10장 저장
- [ ] 결과 정리 (`results/baseline.md`)

### Phase 2
- [ ] `landmark_heatmap.py` 작성 + 단위 테스트
- [ ] 랜드마크 사전 계산 (24K, MediaPipe)
- [ ] `data.py` 4채널 지원 + 테스트
- [ ] `unet.py` in_channels 인자 + 테스트
- [ ] `config.yaml` 확장
- [ ] 1 epoch sanity check (loss 감소 확인)

### Phase 3
- [ ] config: use_landmark=true, in_channels=4
- [ ] 학습 (50분)
- [ ] Test mIoU 측정
- [ ] 예측 시각화 10장

### Phase 4
- [ ] 비교 표 작성
- [ ] 정성 비교 5장 (Baseline vs LM-guided)
- [ ] 의사결정 (시나리오 A/B/C/D)
- [ ] Week 3 후반 일정 확정

---

## 8. plan v0.1 → v0.2 → 구현

1. **현재 plan v0.1** — 너 검토
2. 메모 / 피드백 → "메모 반영해서 v0.2 만들어 줘. **아직 구현하지 마**"
3. v0.2 최종 승인 → "Phase 1 시작" 지시
4. Phase 1 완료 후 결과 보고 → Phase 2 진행 결정

---

## 9. 발표 자료 영향 (Week 4)

이 plan대로 진행하면 발표 슬라이드 6번 + 8번에 다음 추가 가능:

### 슬라이드 6번 (모델 설계) 추가
```
[Baseline U-Net → LM-guided U-Net]
- MediaPipe 478점 → Gaussian heatmap → 4번째 입력 채널
- 도메인 지식을 모델에 직접 주입
- Skip Connection 그대로 (검증된 구조)
```

### 슬라이드 8번 (성능 분석) 추가
```
[Baseline vs LM-guided 비교]
┌──────────────────┬──────────┬──────────┐
│ Model            │ mIoU     │ Δ        │
├──────────────────┼──────────┼──────────┤
│ Baseline U-Net   │ 0.79     │ —        │
│ + LM-guided ★   │ 0.83     │ +4.0%p   │
└──────────────────┴──────────┴──────────┘
```

→ "**Baseline 대비 +4%p**" 한 줄로 강화 효과 정량 어필.

---

*plan v0.1 끝. 검토 후 피드백 줘. 구현은 v0.2 확정 후 Phase 1부터 시작.*
