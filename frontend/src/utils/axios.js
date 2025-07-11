import axios from "axios";
import { API_BASE_URL } from "@/assets/config";

const instance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// เพิ่ม token อัตโนมัติในทุก request
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ตรวจจับ token หมดอายุ
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login"; // redirect อัตโนมัติ
    }
    return Promise.reject(error);
  }
);

export default instance;
