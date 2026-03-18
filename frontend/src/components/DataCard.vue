<template>
  <div :class="['data-card', { interactive, hoverable }]" @click="handleClick">
    <div v-if="icon || $slots.icon" class="card-icon">
      <slot name="icon">
        <span>{{ icon }}</span>
      </slot>
    </div>
    <div class="card-content">
      <div class="card-value">
        <span v-if="prefix" class="value-prefix">{{ prefix }}</span>
        <span class="value-text">{{ formattedValue }}</span>
        <span v-if="suffix" class="value-suffix">{{ suffix }}</span>
      </div>
      <div class="card-label">{{ label }}</div>
      <div v-if="trend || $slots.trend" class="card-trend" :class="trendClass">
        <slot name="trend">
          <span v-if="trend !== null" class="trend-icon">
            <svg v-if="trend > 0" width="12" height="12" viewBox="0 0 12 12">
              <path d="M2 8L6 4L10 8" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else-if="trend < 0" width="12" height="12" viewBox="0 0 12 12">
              <path d="M2 4L6 8L10 4" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="trend-text">{{ Math.abs(trend) }}%</span>
        </slot>
      </div>
    </div>
    <div v-if="loading" class="card-shimmer"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: {
    type: [Number, String],
    required: true
  },
  label: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: ''
  },
  prefix: {
    type: String,
    default: ''
  },
  suffix: {
    type: String,
    default: ''
  },
  trend: {
    type: Number,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  interactive: {
    type: Boolean,
    default: false
  },
  hoverable: {
    type: Boolean,
    default: false
  },
  format: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

const formattedValue = computed(() => {
  if (typeof props.value === 'string') return props.value
  if (props.format) {
    return props.value.toLocaleString()
  }
  return props.value
})

const trendClass = computed(() => {
  if (props.trend === null) return ''
  return props.trend > 0 ? 'positive' : props.trend < 0 ? 'negative' : 'neutral'
})

const handleClick = () => {
  if (props.interactive) {
    emit('click')
  }
}
</script>

<style scoped>
.data-card {
  position: relative;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: 24px;
  border: 1px solid rgba(196, 164, 132, 0.08);
  transition: all var(--transition-base);
  overflow: hidden;
}

.data-card.hoverable:hover {
  box-shadow: var(--shadow-soft);
  border-color: rgba(196, 164, 132, 0.15);
  transform: translateY(-2px);
}

.data-card.interactive {
  cursor: pointer;
}

.card-icon {
  font-size: 32px;
  margin-bottom: 16px;
  opacity: 0.8;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  flex-wrap: wrap;
}

.value-prefix,
.value-suffix {
  font-size: 1rem;
  color: var(--text-tertiary);
}

.value-text {
  font-size: 2rem;
  font-weight: 500;
  font-family: 'Playfair Display', Georgia, serif;
  color: var(--text-primary);
  line-height: 1;
}

.card-label {
  font-size: 12px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  margin-top: 8px;
}

.card-trend.positive {
  color: var(--success);
}

.card-trend.negative {
  color: var(--error);
}

.card-trend.neutral {
  color: var(--text-tertiary);
}

.trend-icon {
  display: flex;
  align-items: center;
}

/* 加载动画 */
.card-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(196, 164, 132, 0.1) 50%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  pointer-events: none;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* 响应式 */
@media (max-width: 480px) {
  .value-text {
    font-size: 1.5rem;
  }
}
</style>
