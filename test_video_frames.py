import os
import sys
import mlmodel

def test_video_frames(video_path):
    """Test the video_by_frames function with a specific video file."""
    print(f"Testing video_by_frames with: {video_path}")
    print(f"File exists: {os.path.exists(video_path)}")
    
    try:
        # Process the video using our new function
        result = mlmodel.video_by_frames(video_path, max_frames=5)
        
        # Print the results
        print("\nResults:")
        print(f"Label: {result.get('label', 'N/A')}")
        
        # Print confidences
        confidences = result.get('confidences', [])
        for conf in confidences:
            print(f"  {conf.get('label', 'N/A')}: {conf.get('confidence', 0)}")
        
        # Print frame analysis
        frame_analysis = result.get('frame_analysis', {})
        print("\nFrame Analysis:")
        for key, value in frame_analysis.items():
            print(f"  {key}: {value}")
            
        return result
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    # Check if a video path was provided
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        # Use a default video path
        video_path = os.path.join("pics", "world.mp4")
    
    # Run the test
    test_video_frames(video_path) 