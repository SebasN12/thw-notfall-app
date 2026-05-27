<template>
  <section class="page">
    <div>
      <h1 class="page__title">Lager</h1>
      <p class="page__subtitle">
        Lagerstruktur nach Warehouse, Regal, Fach und Produkt.
      </p>
    </div>

    <div class="breadcrumb" v-if="selectedWarehouse || selectedShelf || selectedSlot">
      <span v-if="selectedWarehouse">{{ selectedWarehouse.name }}</span>
      <span v-if="selectedShelf"> / {{ selectedShelf.name }}</span>
      <span v-if="selectedSlot"> / {{ selectedSlot.name }}</span>
    </div>

    <div v-if="selectedSlot" class="toolbar-stack">
      <input
        v-model="productQuery"
        class="search-input"
        type="text"
        placeholder="Produkte im Fach durchsuchen"
      />
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-dots">
        <span></span><span></span><span></span>
      </div>
      <div>Lagerdaten werden geladen ...</div>
    </div>

    <div v-else-if="!selectedWarehouse" class="card-grid">
      <button
        v-for="warehouse in warehouses"
        :key="warehouse.id"
        class="select-card card-tap"
        type="button"
        @click="openWarehouse(warehouse)"
      >
        <span class="select-card__title">{{ warehouse.name }}</span>
        <span class="select-card__text">
          {{ warehouse.shelves.length }} Regale
        </span>
      </button>
    </div>

    <div v-else-if="selectedWarehouse && !selectedShelf" class="page">
      <button class="back-button" type="button" @click="resetToWarehouses">← Alle Lager</button>

      <div class="card-grid">
        <button
          v-for="shelf in selectedWarehouse.shelves"
          :key="shelf.id"
          class="select-card card-tap"
          type="button"
          @click="openShelf(shelf)"
        >
          <span class="select-card__title">{{ shelf.name }}</span>
          <span class="select-card__text">
            {{ shelf.slots.length }} Fächer
          </span>
        </button>
      </div>
    </div>

    <div v-else-if="selectedShelf && !selectedSlot" class="page">
      <button class="back-button" type="button" @click="selectedShelf = null">← Zurück zu Regalen</button>

      <div class="card-grid">
        <button
          v-for="slot in selectedShelf.slots"
          :key="slot.id"
          class="select-card card-tap"
          type="button"
          @click="openSlot(slot)"
        >
          <span class="select-card__title">{{ slot.name }}</span>
          <span class="select-card__text">
            {{ slot.products.length }} Produkte
          </span>
        </button>
      </div>
    </div>

    <div v-else-if="selectedSlot" class="page">
      <button class="back-button" type="button" @click="selectedSlot = null">← Zurück zu Fächern</button>

      <div v-if="filteredProducts.length" class="card-grid">
        <RouterLink
          v-for="product in filteredProducts"
          :key="product.id"
          :to="`/produkt/${product.id}`"
          class="product-card card-tap"
        >
          <div class="product-card__top">
            <div>
              <h2 class="card__title" style="margin-bottom: 4px;">{{ product.name }}</h2>
              <p class="card__text">{{ product.brand }} · {{ product.packSize }}</p>
            </div>
            <span class="mini-badge">{{ product.category }}</span>
          </div>

          <div class="product-card__meta">
            <span><strong>Menge:</strong> {{ product.menge }}</span>
            <span><strong>MHD:</strong> {{ product.mhd }}</span>
          </div>
        </RouterLink>
      </div>

      <div v-else class="empty-state">
        Keine Produkte für die aktuelle Suche gefunden.
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api } from '../services/api'
import type { Product, Shelf, Slot, Warehouse } from '../types'

const loading = ref(true)
const warehouses = ref<Warehouse[]>([])
const selectedWarehouse = ref<Warehouse | null>(null)
const selectedShelf = ref<Shelf | null>(null)
const selectedSlot = ref<Slot | null>(null)
const productQuery = ref('')

onMounted(async () => {
  loading.value = true
  warehouses.value = await api.getWarehouses()
  loading.value = false
})

const filteredProducts = computed<Product[]>(() => {
  const products = selectedSlot.value?.products ?? []
  const q = productQuery.value.trim().toLowerCase()

  if (!q) return products

  return products.filter((product) =>
    [product.name, product.brand, product.category, product.barcode]
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

function openWarehouse(warehouse: Warehouse): void {
  selectedWarehouse.value = warehouse
  selectedShelf.value = null
  selectedSlot.value = null
  productQuery.value = ''
}

function openShelf(shelf: Shelf): void {
  selectedShelf.value = shelf
  selectedSlot.value = null
  productQuery.value = ''
}

function openSlot(slot: Slot): void {
  selectedSlot.value = slot
  productQuery.value = ''
}

function resetToWarehouses(): void {
  selectedWarehouse.value = null
  selectedShelf.value = null
  selectedSlot.value = null
  productQuery.value = ''
}
</script>