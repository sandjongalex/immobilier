// @vitest-environment jsdom
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import App from './App'

describe('socle React', () => {
  it('affiche le titre sans annonces fictives', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: 'Immobilier' })).toBeTruthy()
  })
})
