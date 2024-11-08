-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 23, 2024 at 12:24 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `chamber_management`
--

-- --------------------------------------------------------

--
-- Table structure for table `tbl_appointments`
--

CREATE TABLE `tbl_appointments` (
  `AppointmentID` varchar(40) NOT NULL,
  `PatientID` varchar(30) DEFAULT NULL,
  `DoctorID` varchar(30) DEFAULT NULL,
  `AppointmentDateTime` datetime DEFAULT NULL,
  `Status` enum('pending','done') DEFAULT 'pending',
  `Notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_appointments`
--

INSERT INTO `tbl_appointments` (`AppointmentID`, `PatientID`, `DoctorID`, `AppointmentDateTime`, `Status`, `Notes`) VALUES
('\'341e38d0cabf4b2d85a017fe6e729a\'', '3cf317c17545460984b35770af8221', '91ddea0408544a7f8561b6415a024a', '2024-08-06 20:00:00', 'done', 'headache'),
('\'39ff108c97a94fbabe8a63ef5fc84e\'', '67fda1e4101c4daf9771c88ce0939d', '91ddea0408544a7f8561b6415a024a', '2024-07-09 15:00:00', 'pending', 'headache'),
('\'7b55ce3e72084eba8c55f24ddd2436\'', '73c158fdbb6c49159875cd611634a7', '91ddea0408544a7f8561b6415a024a', '2024-08-06 16:00:00', 'done', 'stomach pain'),
('\'efeff10d450d44d9b8261493b3eaf4\'', '67fda1e4101c4daf9771c88ce0939d', '91ddea0408544a7f8561b6415a024a', '2024-08-06 15:00:00', 'done', 'headache');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_doctors`
--

CREATE TABLE `tbl_doctors` (
  `DoctorId` varchar(30) NOT NULL,
  `Registration` varchar(8) DEFAULT NULL,
  `Name` varchar(30) DEFAULT NULL,
  `Speciality` varchar(30) DEFAULT NULL,
  `Qualifications` varchar(100) DEFAULT NULL,
  `Phone` varchar(14) DEFAULT NULL,
  `Email` varchar(30) DEFAULT NULL,
  `EmailConfirmed` tinyint(1) DEFAULT 0,
  `Password` varchar(30) DEFAULT NULL,
  `Address` text DEFAULT NULL,
  `ClinicName` varchar(50) DEFAULT NULL,
  `ClinicAddress` text DEFAULT NULL,
  `Availability` tinyint(1) DEFAULT NULL,
  `Fees` int(11) DEFAULT NULL,
  `Notes` text DEFAULT NULL,
  `AppTodo` varchar(1000) DEFAULT NULL,
  `PatTodo` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_doctors`
--

INSERT INTO `tbl_doctors` (`DoctorId`, `Registration`, `Name`, `Speciality`, `Qualifications`, `Phone`, `Email`, `EmailConfirmed`, `Password`, `Address`, `ClinicName`, `ClinicAddress`, `Availability`, `Fees`, `Notes`, `AppTodo`, `PatTodo`) VALUES
('91ddea0408544a7f8561b6415a024a', '47584', 'Ismail', 'test', 'MBBS', '01648334337', 'test', 1, '$2a$08$7tPReH62WK.VKkG59QBx1.Z', 'Cumilla', NULL, 'Sylhet', 0, 500, NULL, '1. this\n2. is', 'done\ndone\nsecond one to go');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_patients`
--

CREATE TABLE `tbl_patients` (
  `PatientId` varchar(30) NOT NULL,
  `DoctorID` varchar(30) DEFAULT NULL,
  `Name` varchar(30) NOT NULL,
  `Age` int(11) DEFAULT NULL,
  `Registration_date` datetime DEFAULT current_timestamp(),
  `DateOfBirth` date DEFAULT NULL,
  `Phone` varchar(15) DEFAULT NULL,
  `Email` varchar(30) DEFAULT NULL,
  `Address` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_patients`
--

INSERT INTO `tbl_patients` (`PatientId`, `DoctorID`, `Name`, `Age`, `Registration_date`, `DateOfBirth`, `Phone`, `Email`, `Address`) VALUES
('3cf317c17545460984b35770af8221', '91ddea0408544a7f8561b6415a024a', 'Farzin', 22, '2024-08-06 12:19:40', '2002-07-02', '0173238', 'test@gmail.com', 'unknown'),
('4bbef2cba34e45bba6967131611d8e', '91ddea0408544a7f8561b6415a024a', 'Pinku', 8, '2024-07-09 13:24:26', '2016-06-02', '01683456342', 'imrujnila@gmail.com', 'Cumilla'),
('67fda1e4101c4daf9771c88ce0939d', '91ddea0408544a7f8561b6415a024a', 'Sawon', 23, '2024-07-09 13:31:38', '2001-06-02', '01683456342', 'imrujnila@gmail.com', 'Noakhali'),
('73c158fdbb6c49159875cd611634a7', '91ddea0408544a7f8561b6415a024a', 'Rinku', 23, '2024-07-09 13:23:01', '2001-06-02', '01683456342', 'shakibshakib0504@gmail.com', 'Sylhet');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_prescription`
--

CREATE TABLE `tbl_prescription` (
  `PrescriptionID` varchar(30) NOT NULL,
  `PatientID` varchar(30) DEFAULT NULL,
  `DoctorID` varchar(30) DEFAULT NULL,
  `DateIssued` datetime DEFAULT NULL,
  `MedicationName` varchar(255) DEFAULT NULL,
  `Dosage` varchar(50) DEFAULT NULL,
  `Frequency` varchar(50) DEFAULT NULL,
  `Duration` varchar(50) DEFAULT NULL,
  `Status` enum('Active','Expired','Filled') DEFAULT NULL,
  `Instructions` text DEFAULT NULL,
  `PrescriptionNotes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tbl_prescription`
--

INSERT INTO `tbl_prescription` (`PrescriptionID`, `PatientID`, `DoctorID`, `DateIssued`, `MedicationName`, `Dosage`, `Frequency`, `Duration`, `Status`, `Instructions`, `PrescriptionNotes`) VALUES
('117d57af6217494a89f9762f508876', '3cf317c17545460984b35770af8221', '91ddea0408544a7f8561b6415a024a', '2024-08-06 21:19:29', 'ibuprofen', '200mg', 'every 4 hours', '2 days', 'Active', 'None', 'None'),
('164eda5f06df4caebd96b8e0cd6396', '4bbef2cba34e45bba6967131611d8e', '91ddea0408544a7f8561b6415a024a', '2024-07-10 16:23:18', 'Paracetamol', '500mg', 'twice a day', '5 days', 'Active', 'take with food', ''),
('5555aa3dbc814c36b0d40b9c2ba013', '3cf317c17545460984b35770af8221', '91ddea0408544a7f8561b6415a024a', '2024-08-06 21:01:39', 'Ibuprofen', '200mg', 'each day', '2 days', 'Active', 'be aware of depression', ' '),
('6f2d4f22206a443badc66dd5ac02d2', '3cf317c17545460984b35770af8221', '91ddea0408544a7f8561b6415a024a', '2024-08-06 21:01:41', 'Ibuprofen', '200mg', 'each day', '2 days', 'Active', 'be aware of depression', ' '),
('eba1b7411077484ca32995fc49c34c', '67fda1e4101c4daf9771c88ce0939d', '91ddea0408544a7f8561b6415a024a', '2024-08-06 05:25:14', 'paracetamol', ' 500mg', 'twice daily', ' 7 days', 'Active', 'avoid cold water', 'test');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tbl_appointments`
--
ALTER TABLE `tbl_appointments`
  ADD PRIMARY KEY (`AppointmentID`),
  ADD KEY `PatientID` (`PatientID`),
  ADD KEY `DoctorID` (`DoctorID`);

--
-- Indexes for table `tbl_doctors`
--
ALTER TABLE `tbl_doctors`
  ADD PRIMARY KEY (`DoctorId`);

--
-- Indexes for table `tbl_patients`
--
ALTER TABLE `tbl_patients`
  ADD PRIMARY KEY (`PatientId`),
  ADD KEY `DoctorID` (`DoctorID`);

--
-- Indexes for table `tbl_prescription`
--
ALTER TABLE `tbl_prescription`
  ADD PRIMARY KEY (`PrescriptionID`),
  ADD KEY `PatientID` (`PatientID`),
  ADD KEY `DoctorID` (`DoctorID`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tbl_appointments`
--
ALTER TABLE `tbl_appointments`
  ADD CONSTRAINT `tbl_appointments_ibfk_1` FOREIGN KEY (`PatientID`) REFERENCES `tbl_patients` (`PatientId`),
  ADD CONSTRAINT `tbl_appointments_ibfk_2` FOREIGN KEY (`DoctorID`) REFERENCES `tbl_doctors` (`DoctorId`);

--
-- Constraints for table `tbl_patients`
--
ALTER TABLE `tbl_patients`
  ADD CONSTRAINT `tbl_patients_ibfk_1` FOREIGN KEY (`DoctorID`) REFERENCES `tbl_doctors` (`DoctorId`);

--
-- Constraints for table `tbl_prescription`
--
ALTER TABLE `tbl_prescription`
  ADD CONSTRAINT `tbl_prescription_ibfk_1` FOREIGN KEY (`PatientID`) REFERENCES `tbl_patients` (`PatientId`),
  ADD CONSTRAINT `tbl_prescription_ibfk_2` FOREIGN KEY (`DoctorID`) REFERENCES `tbl_doctors` (`DoctorId`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
