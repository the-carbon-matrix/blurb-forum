import { useAuthStore } from "@/stores/auth";
import { createRouter, createWebHistory } from "vue-router";

import LoginView from "@/views/Login.vue";
import RegisterView from "@/views/Register.vue";
import AdminView from "@/views/Admin.vue";
import FeedView from "@/views/Feed.vue";
import PostView from "@/views/Post.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/login", component: LoginView },
    { path: "/register", component: RegisterView },
    {
      path: "/admin",
      component: AdminView,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: "/feed",
      component: FeedView,
      meta: { requiresAuth: true, requiresMember: true },
    },
    {
      path: "/post",
      component: PostView,
      meta: { requiresAuth: true, requiresMember: true },
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  if (!auth.ready) await auth.restoreSession();

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  if (to.path === "/login" && auth.isAuthenticated) {
    return { path: "/" };
  }

  if (to.path === "/") {
    if (auth.user?.roles?.includes("admin")) return { path: "/admin" };
    if (auth.user?.roles?.includes("member")) return { path: "/feed" };
    return { path: "/login" };
  }

  if (to.meta.requiresAdmin && !auth.user?.roles?.includes("admin"))
    return { path: "/" };
  if (to.meta.requiresMember && !auth.user?.roles?.includes("member"))
    return { path: "/" };
});

export default router;
