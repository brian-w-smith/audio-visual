import numpy as np
import soundfile as sf
import panda3d.core as p3d
from panda3d.core import WindowProperties
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import os
import simpleaudio as sa

class AudioVisualizer(ShowBase):
    def __init__(self, audio_file):
        """
        Initialize Panda3D audio visualization
        
        Args:
            audio_file (str): Path to the audio file
        """
        # Initialize Panda3D
        super().__init__()
        props = WindowProperties()
        props.setTitle("Audio Visualizer")
        self.win.requestProperties(props)
        
        # Disable mouse control
        self.disableMouse()
        
        # Load audio file
        self.audio_file = audio_file
        
        # Read audio data
        try:
            self.audio_data, self.sample_rate = sf.read(audio_file)
        except Exception as e:
            print(f"Error loading audio file: {e}")
            self.audio_data = np.zeros(1024)  # Fallback empty audio
            self.sample_rate = 44100
        
        # Convert to mono if stereo
        if self.audio_data.ndim > 1:
            self.audio_data = self.audio_data.mean(axis=1)
        
        # Convert to 16-bit integer for playback
        self.playback_data = (self.audio_data * 32767).astype(np.int16)
        
        # Start audio playback
        self.play_audio()
        
        # Setup the scene
        self.setup_scene()
        
        # Prepare visualization
        self.prepare_bars()
        
        # Add update task
        self.taskMgr.add(self.update_visualization, "UpdateVisualization")
    
    def play_audio(self):
        """
        Play the audio file
        """
        try:
            # Play audio
            self.playback_obj = sa.play_buffer(
                self.playback_data, 
                1,  # 1 channel (mono)
                2,  # 2 bytes per sample (16-bit)
                self.sample_rate
            )
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def setup_scene(self):
        """
        Set up the basic 3D scene
        """
        # Position camera
        self.camera.setPos(0, -48, 0)
        self.camera.lookAt(0, 0, 0)
        
        # Add some basic lighting
        ambient_light = p3d.AmbientLight('ambient')
        ambient_light.setColor((0.2, 0.2, 0.2, 1))
        ambient_np = self.render.attachNewNode(ambient_light)
        self.render.setLight(ambient_np)
        
        directional_light = p3d.DirectionalLight('directional')
        directional_light.setColor((0.8, 0.8, 0.8, 1))
        directional_np = self.render.attachNewNode(directional_light)
        directional_np.setHpr(45, -45, 0)
        self.render.setLight(directional_np)
    
    def prepare_bars(self):
        """
        Create visualization bars
        """
        # Number of bars
        self.num_bars = 64
        self.bars = []
        
        # Create bars
        for i in range(self.num_bars):
            # Create a box for each bar
            bar = self.loader.loadModel("misc/rgbCube")
            
            # Position bars in a line
            x_pos = (i - self.num_bars/2) * 0.5
            bar.setPos(x_pos, 0, 0)
            
            # Set initial scale
            bar.setScale(0.4, 0.1, 0.1)
            
            # Color based on position
            bar.setColor(
                1.0, 
                0.5 + (i / self.num_bars), 
                0.2 + (i / self.num_bars), 
                1
            )
            
            # Attach to scene
            bar.reparentTo(self.render)
            self.bars.append(bar)
    
    def update_visualization(self, task):
        """
        Update bar heights based on audio
        """
        # Get audio playback time
        current_time = task.time
        
        # Calculate audio sample position
        start_sample = int(current_time * self.sample_rate)
        
        # Ensure we don't go out of bounds
        if start_sample + self.num_bars >= len(self.audio_data):
            return Task.done
        
        # Extract audio chunk
        chunk = self.audio_data[start_sample:start_sample + self.num_bars]
        
        # Update bar heights
        for i, bar in enumerate(self.bars):
            if i < len(chunk):
                # Scale height based on audio amplitude
                height = abs(chunk[i]) * 10  # Adjust multiplier as needed
                bar.setScale(bar.getScale().x, 0.1, max(0.1, height))
        
        return Task.cont

def main():
    audio_file = 'LTJ Bukem - Atlantis [-g3RUnx9svM].mp3'
    
    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"Error: File not found - {audio_file}")
        print("Please update the audio_file path in the script")
        return
    
    # Create and run visualization
    app = AudioVisualizer(audio_file)
    app.run()

# Installation instructions
print("Required libraries:")
print("pip install numpy soundfile panda3d simpleaudio")

# Uncomment to run
if __name__ == '__main__':
    main()
