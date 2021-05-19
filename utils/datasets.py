import cv2
class webcam: 
    def __init__(self, sources='0'):
        try:
            self.cap = cv2.VideoCapture(int(sources))
        except:
            self.cap = cv2.VideoCapture(s)
        assert self.cap.isOpened(), 'Failed to open %s' % s
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS) % 100
        _, self.img = self.cap.read()  
        print('success (%gx%g at %.2f FPS)\n' % (w, h, fps))
    def __iter__(self):
        self.count = -1
        return self
    def __next__(self):
        self.count += 1
        ret, self.img = self.cap.read()
        assert ret, "Camera Error"
        self.img = cv2.flip(self.img, 1)  
        if cv2.waitKey(1) == ord('q'):  
            cv2.destroyAllWindows()
            raise StopIteration
        return self.img
    def __len__(self):
        return 0 
