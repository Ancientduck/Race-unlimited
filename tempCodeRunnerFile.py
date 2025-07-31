def find_Spawn(self): #trying the new thing. getting numpy error axis aerror 2 is out of bounds
         # Load image
        im = cv2.imread(self.road_image)

        # Define the blue colour we want to find - remember OpenCV uses BGR ordering
        red = [255,0,0]

        # Get X and Y coordinates of all blue pixels
        Y, X = np.where(np.all(im==red,axis=2))

        print(X,Y)