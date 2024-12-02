import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

const EditProfile = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    bio: "",
    birthday: "",
    profile_picture: null,
    current_password: "",
    new_password: "",
    retyped_new_password: "",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // Authentication guard
  useEffect(() => {
    const accessToken = localStorage.getItem("access");
    if (!accessToken) {
      navigate("/login"); // Redirect to login if not authenticated
    }
  }, [navigate]);

  // Fetch current profile data
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get("/profile/", {
          headers: { Authorization: `Bearer ${localStorage.getItem("access")}` },
        });
        setFormData({
          username: response.data.name,
          email: response.data.email,
          first_name: response.data.name,
          last_name: response.data.surname,
          bio: response.data.bio,
          birthday: response.data.birthday || "",
          profile_picture: null,
          current_password: "",
          new_password: "",
          retyped_new_password: "",
        });
      } catch (err) {
        setError("Failed to load profile data.");
      }
    };
    fetchProfile();
  }, []);

  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // Handle file upload changes
  const handleFileChange = (e) => {
    setFormData({ ...formData, profile_picture: e.target.files[0] });
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    const data = new FormData(); // Using FormData for file uploads
    for (let key in formData) {
      if (formData[key] !== null) data.append(key, formData[key]);
    }

    try {
      const response = await api.put("/edit-profile/", data, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access")}`,
          "Content-Type": "multipart/form-data",
        },
      });
      setMessage(response.data.message);
    } catch (err) {
      setError(err.response?.data?.error || "An error occurred while updating your profile.");
    }
  };

  return (
    <div>
      <h2>Edit Profile</h2>
      {message && <p style={{ color: "green" }}>{message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit} encType="multipart/form-data">
        <input
          type="text"
          name="username"
          value={formData.username}
          placeholder="Username"
          onChange={handleChange}
        />
        <input
          type="email"
          name="email"
          value={formData.email}
          placeholder="Email"
          onChange={handleChange}
        />
        <input
          type="text"
          name="first_name"
          value={formData.first_name}
          placeholder="First Name"
          onChange={handleChange}
        />
        <input
          type="text"
          name="last_name"
          value={formData.last_name}
          placeholder="Last Name"
          onChange={handleChange}
        />
        <textarea
          name="bio"
          value={formData.bio}
          placeholder="Bio"
          onChange={handleChange}
        />
        <input
          type="date"
          name="birthday"
          value={formData.birthday}
          onChange={handleChange}
        />
        <input
          type="file"
          name="profile_picture"
          accept="image/*"
          onChange={handleFileChange}
        />
        <input
          type="password"
          name="current_password"
          placeholder="Current Password"
          onChange={handleChange}
        />
        <input
          type="password"
          name="new_password"
          placeholder="New Password"
          onChange={handleChange}
        />
        <input
          type="password"
          name="retyped_new_password"
          placeholder="Retype New Password"
          onChange={handleChange}
        />
        <button type="submit">Update Profile</button>
      </form>
    </div>
  );
};

export default EditProfile;
