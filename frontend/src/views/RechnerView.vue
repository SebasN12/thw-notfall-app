<template>
  <section class="page">
    <div>
      <h1 class="page__title">Vorratsrechner</h1>
      <p class="page__subtitle">
        Bedarf, Vorrat und Deckungsgrad nach Erzeugnisgruppe.
      </p>
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

        <button type="button" class="primary-button" @click="runCalculation">
          Deckungsgrad berechnen
        </button>
      </div>
    </div>

    <div class="stats-grid" v-if="summary">
      <div class="stat-card">
        <span class="stat-card__label">Gesamt kg Vorrat</span>
        <strong class="stat-card__value">{{ summary.totalAvailableKg }}</strong>
      </div>
      <div class="stat-card">
        <span class="stat-card__label">Personentage (kcal)</span>
        <strong class="stat-card__value">{{ summary.personDaysByCalories }}</strong>
      </div>
    </div>

    <div class="card" v-if="rows.length">
      <h2 class="card__title">Ergebnis nach Erzeugnisgruppe</h2>

      <div class="result-list">
        <div v-for="row in rows" :key="row.category" class="result-item">
          <div class="result-item__top">
            <div>
              <div class="result-item__title">{{ row.category }}</div>
              <div class="result-item__meta">
                Bedarf {{ row.requiredKg }} kg · Vorrat {{ row.availableKg }} kg
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

    <div class="card" v-if="summary">
      <h2 class="card__title">Gesamtbewertung</h2>
      <p class="card__text">
        Der aktuelle Vorrat reicht rechnerisch für
        <strong>{{ summary.personDaysByCalories }}</strong> Personentage auf Basis
        einer groben Energiebewertung mit 2200 kcal pro Person und Tag.
      </p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../services/api'
import type { CalculatorResultRow, CalculatorSummary } from '../types'

const persons = ref<number>(50)
const days = ref<number>(14)
const rows = ref<CalculatorResultRow[]>([])
const summary = ref<CalculatorSummary | null>(null)

async function runCalculation(): Promise<void> {
  const p = persons.value ?? 0
  const d = days.value ?? 0

  if (p < 1 || d < 1) return

  const result = await api.calculateCoverage(p, d)
  rows.value = result.rows
  summary.value = result.summary
}

onMounted(async () => {
  await runCalculation()
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