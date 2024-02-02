import noise
import numpy as np
import matplotlib.pyplot as plt

def generate_perlin_worm_cave(width, height, scale, octaves, persistence, lacunarity, seed):
    cave_noise = np.zeros((width, height))

    for i in range(width):
        for j in range(height):
            x = i / scale
            y = j / scale

            # Adjust the coordinates to create cave-like structures
            x += 10.0 * np.sin(y * 0.1)
            y += 10.0 * np.sin(x * 0.1)

            # Generate Perlin worm noise at the specified coordinates
            value = noise.pnoise2(x, y, octaves=octaves, persistence=persistence, lacunarity=lacunarity, repeatx=1024, repeaty=1024, base=seed)
            cave_noise[i][j] = value

    return cave_noise

# Example parameters for cave generation
width, height = 1000, 500
scale = 30
octaves = 6
persistence = 0.5
lacunarity = 2.0
seed = 42

# Generate Perlin worm cave noise
cave_noise = generate_perlin_worm_cave(width, height, scale, octaves, persistence, lacunarity, seed)

# Display the generated noise as an image
plt.imshow(cave_noise, cmap='gray', origin='upper', extent=[0, width, 0, height])
plt.colorbar()
plt.title('Perlin Worm Cave Noise')
plt.show()
