import noise
import numpy as np
import matplotlib.pyplot as plt

def generate_ridged_multifractal(width, height, octaves, lacunarity, persistence, scale):
    world = np.zeros((width, height))

    for i in range(width):
        for j in range(height):
            world[i][j] = noise.pnoise2(i / scale,
                                         j / scale,
                                         octaves=octaves,
                                         lacunarity=lacunarity,
                                         persistence=persistence,
                                         repeatx=1024,
                                         repeaty=1024,
                                         base=42) * 0.5 + 0.5

            # Apply ridges
            world[i][j] = abs(world[i][j] * 2 - 1)

            # Apply reverse power function to emphasize lighter values
            world[i][j] = 1 - np.power(1 - world[i][j], 2)

    return world

# Set parameters
width = 512
height = 512
octaves = 6
lacunarity = 2.0
persistence = 0.5
scale = 100.0

# Generate ridged multifractal noise with emphasized lighter values
ridged_noise = generate_ridged_multifractal(width, height, octaves, lacunarity, persistence, scale)

# Display the generated noise in grayscale
plt.imshow(ridged_noise, cmap='gray', interpolation='bilinear', vmin=0, vmax=1)
plt.colorbar()
plt.show()
