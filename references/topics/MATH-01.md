# MATH-01 — Native vectors, coordinate spaces and transforms

When: Movement, aiming, camera, parenting or animation mixes directions, positions or rotations.

Native candidates: `Vector2`, `Vector3`, `Transform2D`, `Transform3D`, `Basis`, `Quaternion`, `Node2D`, `Node3D`.

## Approach

Use native vector and transform operations with explicit local/global coordinate meaning; choose appropriate rotation representation/interpolation instead of recreating matrix/vector machinery.

Custom math/transform abstractions that obscure engine coordinate conventions or duplicate built-in operations without a requirement.

## Pitfalls

- Positions in different spaces cannot be compared as though they share an origin.
- Direction vectors and positions have different transformation needs.
- Euler interpolation/order can produce unintended 3D rotation behavior; inspect the native transform/rotation guidance.

## Verify

- Exercise the nominated movement/aim under translated/rotated parents.
- Check equivalent world-space behavior in the actual 2D/3D scene.
- Test the required rotation path rather than inferring correctness from a static pose.

## Version and limits

4.7 introductory math and 3D transform docs inspected; no numeric/physics runtime case executed.

## Primary sources


- [FD13: Vector math](https://docs.godotengine.org/en/4.7/tutorials/math/vector_math.html). Scope/limits: Introductory source reading only; not a complete mathematics or runtime correctness audit.

- [FD14: Matrices and transforms](https://docs.godotengine.org/en/4.7/tutorials/math/matrices_and_transforms.html). Scope/limits: Introductory source reading only; not a complete mathematics or runtime correctness audit.

- [FD15: Using 3D transforms](https://docs.godotengine.org/en/4.7/tutorials/3d/using_transforms.html). Scope/limits: Introductory source reading only; not a complete mathematics or runtime correctness audit.
