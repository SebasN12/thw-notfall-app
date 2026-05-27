import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import LagerView from '../views/LagerView.vue'
import RechnerView from '../views/RechnerView.vue'
import WarnungenView from '../views/WarnungenView.vue'
import ProduktDetailView from '../views/ProduktDetailView.vue'
import BarcodeFlowView from '../views/BarcodeFlowView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView,
  },
  {
    path: '/lager',
    name: 'lager',
    component: LagerView,
  },
  {
    path: '/rechner',
    name: 'rechner',
    component: RechnerView,
  },
  {
    path: '/warnungen',
    name: 'warnungen',
    component: WarnungenView,
  },
  {
    path: '/produkt/:id',
    name: 'produkt-detail',
    component: ProduktDetailView,
  },
  {
    path: '/einlagerung',
    name: 'einlagerung',
    component: BarcodeFlowView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router