import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import authRoutes from './auth';

const routes = [
  {
	path: "/",
	name: "Home",
	component: Home,
  },
  ...authRoutes,
];

const router = createRouter({
  base: "/oneinbox_whatsapp/",
  history: createWebHistory(),
  routes,
});

export default router;
