<template>
  <section class="page">
    <div>
      <h1 class="page__title">Vorratsrechner</h1>
      <p class="page__subtitle">
        Bedarf, Vorrat und Deckungsgrad nach Erzeugnisgruppe.
      </p>
    </div>

    <div class="soft-card" v-if="selectedOrtsverband">
      <h3 class="soft-card__title">Aktueller Ortsverband</h3>
      <p class="soft-card__text">{{ selectedOrtsverband.name }}</p>
    </div>

    <div class="card">
      <h2 class="card__title">Eingabe</h2>

      <div class="form-stack" style="margin-top: 12px;">
        <div>
          <label class="field-label">Anzahl Personen</label>
          <input
            v-model.number="persons"
            class="text-input"
            type="number"
            min="1"
            placeholder="z. B. 50"
          />
        </div>

        <div>
          <label class="field-label">Versorgungsdauer in Tagen</label>
          <input
            v-model.number="days"
            class="text-input"
            type="number"
            min="1"
            placeholder="z. B. 14"
          />
        </div>

        <button
          type="button"
          class="primary-button"
          :disabled="loading"
          @click="runCalculation"
        >
          {{ loading ? 'Berechnung läuft ...' : 'Deckungsgrad berechnen' }}
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="empty-state">
      {{ errorMessage }}

      <div class="top-space-sm" v-if="!selectedOrtsverband">
        <RouterLink to="/" class="primary-button" style="display: inline-block;">
          Zum Dashboard
        </RouterLink>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-dots">
        <span></span><span></span><span></span>
      </div>
      <div>Vorratsrechnung wird durchgeführt ...</div>
    </div>

    <div class="stats-grid" v-if="summary && !loading">
      <div class="stat-card">
        <span class="stat-card__label">Gesamtbestand</span>
        <strong class="stat-card__value">{{ summary.totalAvailableKg }}</strong>
      </div>

      <div class="stat-card">
        <span class="stat-card__label">Personentage</span>
        <strong class="stat-card__value">{{ summary.personDaysByCalories }}</strong>
      </div>

      <div class="stat-card" v-if="overallStatus">
        <span class="stat-card__label">Gesamtstatus</span>
        <strong class="stat-card__value">
          {{ overallStatusLabel }}
        </strong>
      </div>
    </div>

    <div class="card" v-if="rows.length && !loading">
      <h2 class="card__title">Ergebnis nach Erzeugnisgruppe</h2>

      <div class="result-list">
        <div v-for="row in rows" :key="row.category" class="result-item">
          <div class="result-item__top">
            <div>
              <div class="result-item__title">{{ row.category }}</div>
              <div class="result-item__meta">
                Bedarf {{ row.requiredKg }} · Vorrat {{ row.availableKg }}
              </div>
            </div>

            <span class="inline-status" :class="coverageClass(row.status)">
              {{ row.coveragePercent }} %
            </span>
          </div>

          <div class="progress">
            <div
              class="progress__bar"
              :class="progressClass(row.status)"
              :style="{ width: `${Math.min(row.coveragePercent, 100)}%` }"
            />
          </div>

          <div class="result-item__hint">
            {{ statusText(row.status) }}
          </div>
        </div>
      </div>
    </div>

    <div class="card" v-if="backendSummary && !loading">
      <h2 class="card__title">Gesamtbewertung</h2>
      <p class="card__text">
        {{ backendSummary }}
      </p>
    </div>

    <div class="soft-card" v-if="summary && !loading">
      <h3 class="soft-card__title">Hinweis zur Berechnung</h3>
      <p class="soft-card__text">
        Die Berechnung basiert auf den im Backend hinterlegten Mindestmengen,
        aktuellen Beständen und einer Energiebewertung mit 2200 kcal pro Person
        und Tag.
      </p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { CalculatorResultRow, CalculatorSummary } from '../types'
import { calculateSupply } from '../services/supplyApi'
import { useOrtsverbandStore } from '../stores/ortsverbandStore'

const persons = ref<number>(50)
const days = ref<number>(14)

const rows = ref<CalculatorResultRow[]>([])
const summary = ref<CalculatorSummary | null>(null)
const backendSummary = ref('')
const overallStatus = ref<'green' | 'yellow' | 'red' | null>(null)

const loading = ref(false)
const errorMessage = ref('')

const {
  selectedOrtsverband,
  loadSelectedOrtsverband,
} = useOrtsverbandStore()

onMounted(async () => {
  loadSelectedOrtsverband()

  if (selectedOrtsverband.value) {
    await runCalculation()
  }
})

async function runCalculation(): Promise<void> {
  const p = persons.value ?? 0
  const d = days.value ?? 0

  if (p < 1 || d < 1) {
    errorMessage.value = 'Bitte gib mindestens eine Person und mindestens einen Tag ein.'
    return
  }

  loadSelectedOrtsverband()

  if (!selectedOrtsverband.value) {
    errorMessage.value = 'Bitte zuerst im Dashboard einen Ortsverband auswählen.'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const result = await calculateSupply(
      selectedOrtsverband.value.id,
      p,
      d,
    )

    rows.value = result.rows
    summary.value = result.summary
    backendSummary.value = result.backendSummary
    overallStatus.value = result.overallStatus
  } catch (error) {
    console.error(error)
    errorMessage.value = 'Der Vorratsrechner konnte nicht geladen werden.'
  } finally {
    loading.value = false
  }
}

const overallStatusLabel = computed(() => {
  if (overallStatus.value === 'green') return 'Grün'
  if (overallStatus.value === 'yellow') return 'Gelb'
  if (overallStatus.value === 'red') return 'Rot'
  return '–'
})

function coverageClass(status: 'green' | 'yellow' | 'red'): string {
  if (status === 'green') return 'inline-status--success'
  if (status === 'yellow') return 'inline-status--warning'
  return 'inline-status--danger'
}

function progressClass(status: 'green' | 'yellow' | 'red'): string {
  if (status === 'green') return 'progress__bar--green'
  if (status === 'yellow') return 'progress__bar--yellow'
  return 'progress__bar--red'
}

function statusText(status: 'green' | 'yellow' | 'red'): string {
  if (status === 'green') return 'Ausreichend versorgt'
  if (status === 'yellow') return 'Knapp unter Soll'
  return 'Kritisch unterversorgt'
}
</script>