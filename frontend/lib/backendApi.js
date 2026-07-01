import axios from 'axios';

// Create an Axios instance with a predefined configuration
const backendApi = axios.create({
  // baseURL: 'http://52.14.111.23',
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,

    // baseURL: "http://127.0.0.1:8000",


    // 👈 PublicIP of your EC2 instance
  withCredentials: true,          // Ensures cookies (like CSRF token) are sent
  headers: {
    // 'Content-Type': 'application/json',
  },
});

// Request interceptor — auto Authorization header + auto trailing slash
backendApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Token ${token}`;
    }

    // Django URLs require a trailing slash. Missing slashes trigger a
    // redirect that drops CORS headers when behind ngrok/production,
    // causing "blocked by CORS policy" errors that look like a CORS
    // misconfig but are actually just a missing "/".
    if (config.url && !config.url.includes('?') && !config.url.endsWith('/')) {
      config.url += '/';
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (optional for global error handling)
backendApi.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error)
);

export default backendApi;

// import axios from 'axios';

// // Create an Axios instance with a predefined configuration
// const backendApi = axios.create({
//   // baseURL: 'http://52.14.111.23',
//   baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,

//     // baseURL: "http://127.0.0.1:8000",


//     // 👈 PublicIP of your EC2 instance
//   withCredentials: true,          // Ensures cookies (like CSRF token) are sent
//   headers: {
//     // 'Content-Type': 'application/json',
//   },
// });

// // Request interceptor to add Authorization token
// backendApi.interceptors.request.use(
//   (config) => {
//     const token = localStorage.getItem('authToken');
//     if (token) {
//       config.headers['Authorization'] = `Token ${token}`;
//     }
//     return config;
//   },
//   (error) => Promise.reject(error)
// );

// // Response interceptor (optional for global error handling)
// backendApi.interceptors.response.use(
//   (response) => response,
//   (error) => Promise.reject(error)
// );

// export default backendApi;


