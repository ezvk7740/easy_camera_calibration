from utils.datasets import webcam
import time
import os
import curses
import numpy as np
import cv2

def main(dataset, outpath):
    stdscr = curses.initscr()
    imgs = []
    obj_points = []
    img_points = []
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= square_size
    def curses_main(stdscr):
        k = ""
        status_found = False
        status = None
#        stdscr.nodelay(1)
        curses.halfdelay(1)
        curses.noecho()
        for im0 in dataset:
            stdscr.clear()
            stdscr.addstr("Press \"j\" to use detected values\n")
            stdscr.addstr("Press \"q\" to end\n")
            stdscr.addstr("Found chessboard: {0}\n".format(str(status_found)))
            if isinstance(k, int) and k != -1:
                stdscr.addstr("Detected key: {0}\n".format(chr(k)))
            else:
                stdscr.addstr("Detected key: None\n")
            print("finding chessboardcorners\n")

            img_gray = cv2.cvtColor(im0, cv2.COLOR_RGB2GRAY)
            if gray_images: im0 = img_gray
            found, corners = cv2.findChessboardCorners(img_gray,
                                                       pattern_size,
                                                       flags=cv2.CALIB_CB_ADAPTIVE_THRESH)
            if found:
                status_found = True
                term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
                cv2.cornerSubPix(img_gray, corners, (5, 5), (-1, -1), term)
                cv2.drawChessboardCorners(im0, pattern_size, corners, found)
                add_corners = corners.reshape(-1,2)
            else:
                status_found = False

            cv2.imshow("Camera Display", im0)

            if k == ord('q'):
                break
            elif k == ord('j'):
                img_points.append(add_corners)
                obj_points.append(pattern_points)
                imgs.append(im0)
            k = stdscr.getch()

    curses.wrapper(curses_main)

    assert len(img_points) != 0, "No Chessboard Corners Added"
    h, w = imgs[0].shape[:2] 
    rms, camera_matrix, dist_coefs, _rvecs, _tvecs = cv2.calibrateCamera(obj_points,
                                                                         img_points,
                                                                         (w, h),
                                                                         None,
                                                                         None)
    with open('{0}.npy'.format(cparams_fn), 'wb') as f:
        np.save(f, rms)
        np.save(f, camera_matrix)
        np.save(f, dist_coefs)
        print('camera intrinsic parameters saved to {0}.npy'.format(cparams_fn))
    undistort_img(imgs, outpath, rms, camera_matrix, dist_coefs, crop_dist)

def undistort_img(imgs, outpath, rms, camera_matrix, dist_coefs, crop_dist):
    print("\nRMS:", rms)
    print("camera matrix:\n", camera_matrix)
    print("distortion coefficients: \n\n", dist_coefs.ravel())
    img_id = 0
    for im in imgs:
        cv2.imwrite(os.path.join(outpath, "{0}.jpg".format(img_id)), im)
        outfile = os.path.join(outpath, '{0}_undistorted.jpg'.format(img_id))
        h, w = im.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))
        dst = cv2.undistort(im, camera_matrix, dist_coefs, None, newcameramtx)
        if crop_dist:
            x, y, w, h = roi
            dst = dst[y:y+h, x:x+w]
        cv2.imwrite(outfile, dst)
        print('undistorted image written to: %s' % outfile)
        img_id += 1
    print('Done')

if __name__ == "__main__":
    outpath = "output"
    crop_dist = False
    cparams_fn = "camera_data"
    pattern_size = (15, 21)
    square_size = 1.0
    gray_images = False
    dataset = webcam('0')
    main(dataset, outpath)
