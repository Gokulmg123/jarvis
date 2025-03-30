import cv2
import face_recognition

def recognize_face():
    known_face_encodings = []
    known_face_names = []

    # Load and encode known face
    known_person1 = face_recognition.load_image_file(r"Data\facedetection\WIN_20250316_21_22_30_Pro.jpg")
    known_person1_encoding = face_recognition.face_encodings(known_person1)[0]

    known_face_encodings.append(known_person1_encoding)
    known_face_names.append("Gokul")

    video_capture = cv2.VideoCapture(0)

    detected_name = "Unknown"

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                detected_name = name  # Store detected name
                
                # Draw box and label
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"Welcome {name}!", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
                cv2.imshow("Face Recognition", frame)
                cv2.waitKey(2000)  # Show message for 2 seconds

                # Exit immediately after detecting a known face
                video_capture.release()
                cv2.destroyAllWindows()
                return detected_name  

        cv2.imshow("video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Allow exit with 'q' key
            break

    video_capture.release()
    cv2.destroyAllWindows()

    return detected_name  # Return the recognized name

if __name__ == "__main__":
    person_name = recognize_face()
    print(f"Detected Person: {person_name}")  # Print name after detection
