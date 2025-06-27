import { createRouter, createWebHistory } from "vue-router";
import login from "../views/login/Login.vue";
import home from '../views/home/Home.vue'
import home_view from '../views/home/Home_View.vue'
import users from '../views/users/Users.vue'
import users_view from '../views/users/Users_View.vue'

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: login },
  { path: "/user", component: users },
  {
    path: '/home',
    component: home,
    children: [
      { path: '', component: home_view },   // 👉 /home = Home.vue
    ]
  },
  {
    path: '/users',
    component: users,
    children: [
      { path: '', component: users_view },   // 👉 /users = Users.vue
    ]
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
