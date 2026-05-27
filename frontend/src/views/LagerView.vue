<template>
  <section class="page">
    <div>
      <h1 class="page__title">Lager</h1>
      <p class="page__subtitle">
        Lagerstruktur nach Lager, Regal, Fach und Produkt.
      </p>
    </div>

    <div class="soft-card" v-if="selectedOrtsverband">
      <h3 class="soft-card__title">Aktueller Ortsverband</h3>
      <p class="soft-card__text">{{ selectedOrtsverband.name }}</p>
    </div>

    <div class="breadcrumb" v-if="selectedLager || selectedRegal || selectedLagerfach">
      <span v-if="selectedLager">{{ selectedLager.name }}</span>
      <span v-if="selectedRegal"> / {{ selectedRegal.bezeichnung }}</span>
      <span v-if="selectedLagerfach"> / Fach {{ selectedLagerfach.position ?? selectedLagerfach.id }}</span>
    </div>

    <div v-if="selectedLagerfach" class="toolbar-stack">
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

    <div v-else-if="errorMessage" class="empty-state">
      {{ errorMessage }}
      <div class="top-space-sm">
        <RouterLink to="/" class="primary-button" style="display: inline-block;">
          Zum Dashboard
        </RouterLink>
      </div>
    </div>

    <!-- Lagerliste -->
    <div v-else-if="!selectedLager" class="card-grid">
      <button
        v-for="lager in lagerListe"
        :key="lager.id"
        class="select-card card-tap"
        type="button"
        @click="openLager(lager)"
      >
        <span class="select-card__title">{{ lager.name ?? `Lager ${lager.id}` }}</span>
        <span class="select-card__text">
          Details anzeigen
        </span>
      </button>

      <div v-if="!lagerListe.length" class="empty-state">
        Für diesen Ortsverband wurden keine Lager gefunden.
      </div>
    </div>

    <!-- Regale -->
    <div v-else-if="selectedLager && !selectedRegal" class="page">
      <button class="back-button" type="button" @click="resetToLagerListe">
        ← Alle Lager
      </button>

      <div class="card-grid">
        <button
          v-for="regal in selectedLager.regale"
          :key="regal.id"
          class="select-card card-tap"
          type="button"
          @click="openRegal(regal)"
        >
          <span class="select-card__title">
            {{ regal.bezeichnung ?? `Regal ${regal.id}` }}
          </span>
          <span class="select-card__text">
            {{ regal.lagerfaecher.length }} Fächer
          </span>
        </button>

        <div v-if="!selectedLager.regale.length" class="empty-state">
          Dieses Lager enthält aktuell keine Regale.
        </div>
      </div>
    </div>

    <!-- Lagerfächer -->
    <div v-else-if="selectedRegal && !selectedLagerfach" class="page">
      <button class="back-button" type="button" @click="selectedRegal = null">
        ← Zurück zu Regalen
      </button>

      <div class="card-grid">
        <button
          v-for="lagerfach in selectedRegal.lagerfaecher"
          :key="lagerfach.id"
          class="select-card card-tap"
          type="button"
          @click="openLagerfach(lagerfach)"
        >
          <span class="select-card__title">
            Fach {{ lagerfach.position ?? lagerfach.id }}
          </span>
          <span class="select-card__text">
            {{ lagerfach.produkte.length }} Produkte
            <span v-if="lagerfach.max_kapazitaet">
              · max. {{ lagerfach.max_kapazitaet }}
            </span>
          </span>
        </button>

        <div v-if="!selectedRegal.lagerfaecher.length" class="empty-state">
          Dieses Regal enthält aktuell keine Lagerfächer.
        </div>
      </div>
    </div>

    <!-- Produkte -->
    <div v-else-if="selectedLagerfach" class="page">
      <button class="back-button" type="button" @click="selectedLagerfach = null">
        ← Zurück zu Fächern
      </button>

      <div v-if="filteredProducts.length" class="card-grid">
        <RouterLink
          v-for="produkt in filteredProducts"
          :key="produkt.stock_id"
          :to="`/produkt/${produkt.stock_id}`"
          class="product-card card-tap"
        >
          <div class="product-card__top">
            <div>
              <h2 class="card__title" style="margin-bottom: 4px;">
                {{ produkt.name ?? 'Unbenanntes Produkt' }}
              </h2>
              <p class="card__text">
                {{ produkt.marke ?? 'Keine Marke' }} · {{ produkt.menge ?? 'Keine Packungsgröße' }}
              </p>
            </div>

            <span class="mini-badge">
              {{ produkt.erzeugnisgruppe ?? 'Sonstiges' }}
            </span>
          </div>

          <div class="product-card__meta">
            <span><strong>Bestand:</strong> {{ produkt.menge_eingelagert ?? 0 }}</span>
            <span><strong>Geöffnet:</strong> {{ produkt.menge_geoeffnet ?? 0 }}</span>
            <span><strong>MHD:</strong> {{ produkt.mhd ?? 'Kein MHD' }}</span>
            <span><strong>Barcode:</strong> {{ produkt.barcode ?? '–' }}</span>
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
import type { LagerDetail, Lagerfach, LagerListItem, Produkt, Regal } from '../types'
import { getWarehouseDetail, getWarehouses } from '../services/lagerApi'
import { useOrtsverbandStore } from '../stores/ortsverbandStore'

const loading = ref(true)
const errorMessage = ref('')

const lagerListe = ref<LagerListItem[]>([])
const selectedLager = ref<LagerDetail | null>(null)
const selectedRegal = ref<Regal | null>(null)
const selectedLagerfach = ref<Lagerfach | null>(null)
const productQuery = ref('')

const {
  selectedOrtsverband,
  loadSelectedOrtsverband,
} = useOrtsverbandStore()

onMounted(async () => {
  await loadLagerListe()
})

async function loadLagerListe(): Promise<void> {
  loading.value = true
  errorMessage.value = ''

  try {
    loadSelectedOrtsverband()

    if (!selectedOrtsverband.value) {
      errorMessage.value = 'Bitte zuerst im Dashboard einen Ortsverband auswählen.'
      return
    }

    lagerListe.value = await getWarehouses(selectedOrtsverband.value.id)
  } catch (error) {
    console.error(error)
    errorMessage.value = 'Lagerdaten konnten nicht geladen werden.'
  } finally {
    loading.value = false
  }
}

async function openLager(lager: LagerListItem): Promise<void> {
  loading.value = true
  errorMessage.value = ''

  try {
    selectedRegal.value = null
    selectedLagerfach.value = null
    productQuery.value = ''

    selectedLager.value = await getWarehouseDetail(lager.id)
  } catch (error) {
    console.error(error)
    errorMessage.value = 'Lagerdetails konnten nicht geladen werden.'
  } finally {
    loading.value = false
  }
}

function openRegal(regal: Regal): void {
  selectedRegal.value = regal
  selectedLagerfach.value = null
  productQuery.value = ''
}

function openLagerfach(lagerfach: Lagerfach): void {
  selectedLagerfach.value = lagerfach
  productQuery.value = ''
}

function resetToLagerListe(): void {
  selectedLager.value = null
  selectedRegal.value = null
  selectedLagerfach.value = null
  productQuery.value = ''
}

const filteredProducts = computed<Produkt[]>(() => {
  const produkte = selectedLagerfach.value?.produkte ?? []
  const q = productQuery.value.trim().toLowerCase()

  if (!q) return produkte

  return produkte.filter((produkt) =>
    [
      produkt.name,
      produkt.marke,
      produkt.erzeugnisgruppe,
      produkt.barcode,
    ]
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})
</script>