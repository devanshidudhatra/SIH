<?php
// Enable error reporting for debugging (disable in production)
// upload.php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

var_dump($_FILES); // Debug: Check if files are being received
var_dump($_POST);  // Debug: Check if any POST data is being received


// Database connection parameters
$servername = "localhost"; // Change if your DB is hosted elsewhere
$username = "your_username"; // Your MySQL username
$password = "your_password"; // Your MySQL password
$dbname = "file_uploads"; // Your database name

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die(json_encode(["status" => "error", "message" => "Connection failed: " . $conn->connect_error]));
}

// Handle file upload
if (isset($_FILES["file"])) {
    $targetDir = "uploads/";
    // Create uploads directory if it doesn't exist
    if (!is_dir($targetDir)) {
        mkdir($targetDir, 0755, true);
    }

    $targetFile = $targetDir . basename($_FILES["file"]["name"]);
    $fileType = strtolower(pathinfo($targetFile, PATHINFO_EXTENSION));

    // Check if the file is a valid format
    $validExtensions = array("jpg", "jpeg", "png", "pdf", "docx");
    if (in_array($fileType, $validExtensions)) {
        if (move_uploaded_file($_FILES["file"]["tmp_name"], $targetFile)) {
            // Prepare and bind the SQL statement
            $stmt = $conn->prepare("INSERT INTO uploads (filename, filetype, filepath) VALUES (?, ?, ?)");
            if ($stmt === false) {
                die(json_encode(["status" => "error", "message" => "Prepare failed: " . $conn->error]));
            }

            $stmt->bind_param("sss", $filename, $filetype, $filepath);

            // Set parameters and execute
            $filename = basename($_FILES["file"]["name"]);
            $filetype = $fileType;
            $filepath = $targetFile;

            if ($stmt->execute()) {
                echo json_encode(["status" => "success", "message" => "File uploaded successfully."]);
            } else {
                echo json_encode(["status" => "error", "message" => "Database insertion failed: " . $stmt->error]);
            }

            // Close the statement and connection
            $stmt->close();
            $conn->close();
        } else {
            echo json_encode(["status" => "error", "message" => "Sorry, there was an error uploading your file."]);
        }
    } else {
        echo json_encode(["status" => "error", "message" => "Invalid file type."]);
    }
} else {
    echo json_encode(["status" => "error", "message" => "No file was uploaded."]);
}
