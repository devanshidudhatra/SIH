<?php
// upload.php
$targetDir = "uploads/";
$targetFile = $targetDir . basename($_FILES["file"]["name"]);
$fileType = strtolower(pathinfo($targetFile, PATHINFO_EXTENSION));

// Check if file is a valid format
$validExtensions = array("jpg", "jpeg", "png", "pdf", "docx");
if (in_array($fileType, $validExtensions)) {
    if (move_uploaded_file($_FILES["file"]["tmp_name"], $targetFile)) {
        // Connect to the database
        $conn = new mysqli("localhost", "username", "password", "database");

        // Check connection
        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }

        // Prepare and bind
        $stmt = $conn->prepare("INSERT INTO uploads (filename, filetype, filepath) VALUES (?, ?, ?)");
        $stmt->bind_param("sss", $filename, $filetype, $filepath);

        // Set parameters and execute
        $filename = basename($_FILES["file"]["name"]);
        $filetype = $fileType;
        $filepath = $targetFile;
        $stmt->execute();

        $stmt->close();
        $conn->close();

        echo json_encode(["status" => "success", "message" => "File uploaded successfully."]);
    } else {
        echo json_encode(["status" => "error", "message" => "Sorry, there was an error uploading your file."]);
    }
} else {
    echo json_encode(["status" => "error", "message" => "Invalid file type."]);
}

