import React, { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../config";

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");

  const token = localStorage.getItem("access");

  useEffect(() => {
    const fetchProfile = async () => { // Corrected function name from fetchuserdata to fetchProfile
      if (!token) {
        setError("No access token found.");
        return;
      }
      try {
        const response = await axios.get(`${API_BASE_URL}/api/profile/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setProfile(response.data);
      } catch (err) {
        setError("Failed to fetch profile.");
      }
    };
    fetchProfile(); // Ensure this function is called
  }, [token]); // Added token as a dependency

  if (error) return <p>{error}</p>;
  if (!profile) return <p>Loading...</p>;

  return (
    <div>
      <h2>Profile</h2>
      <p>Name: {profile.first_name}</p> {/* Changed from profile.name to profile.first_name */}
      <p>Surname: {profile.last_name}</p> {/* Changed from profile.surname to profile.last_name */}
      <p>Email: {profile.email}</p>
      <p>Bio: {profile.bio}</p>
      <p>Birthday: {profile.birthday}</p>
      <img src={profile.profile_picture} alt="Profile" />
    </div>
  );
};

export default Profile;
