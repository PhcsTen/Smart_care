import { createRouter, createWebHistory } from "vue-router";
import login from "../views/login/Login.vue";
import home from "../views/home/Home.vue";
import home_view from "../views/home/Home_View.vue";
import users from "../views/users/Users.vue";
import users_view from "../views/users/Users_View.vue";
import students from "../views/students/Sudents.vue";
import students_view from "../views/students/Students_View.vue";
import years from "../views/years/Years.vue";
import years_view from "../views/years/Years_View.vue";
import classrooms from "../views/classrooms/classrooms.vue";
import classrooms_view from "../views/classrooms/classrooms_View.vue";
import teacher from "../views/teacher/Teacher.vue";
import teacher_view from "../views/teacher/Teacher_View.vue";
import health_records from "../views/health_records/HealthRecords.vue";
import health_records_view from "../views/health_records/HealthRecords_View.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: login },
  { path: "/user", component: users },
  {
    path: "/home",
    component: home,
    children: [
      { path: "", component: home_view }, // 👉 /home = Home.vue
    ],
  },
  {
    path: "/users",
    component: users,
    children: [{ path: "", component: users_view }],
  },
  {
    path: "/students",
    component: students,
    children: [{ path: "", component: students_view }],
  },
  {
    path: "/years",
    component: years,
    children: [{ path: "", component: years_view }],
  },
  {
    path: "/classrooms",
    component: classrooms,
    children: [{ path: "", component: classrooms_view }],
  },
  {
    path: "/teacher",
    component: teacher,
    children: [{ path: "", component: teacher_view }],
  },
  {
    path: "/health",
    component: health_records,
    children: [{ path: "", component: health_records_view }],
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
