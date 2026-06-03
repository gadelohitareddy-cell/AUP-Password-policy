# Camera Route
@app.route('/camera')
def camera():

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:

        success, frame = camera.read()

        # Check if frame loaded properly
        if not success:
            continue

        cv2.imshow("Employee Camera", frame)

        key = cv2.waitKey(1)

        # Press S to save
        if key == ord('s'):

            cv2.imwrite("employee_photo.jpg", frame)

            break

    camera.release()
    cv2.destroyAllWindows()

    return "Photo Captured Successfully"