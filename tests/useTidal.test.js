import { useTidal } from '../src/composables/useTidal.js'

describe('useTidal', () => {
  beforeEach(() => {
    // Reset selectedTracks before each test
    // This assumes useTidal() returns a fresh state or selectedTracks is directly mutable for testing
    const { selectedTracks } = useTidal()
    selectedTracks.value = []
  })

  it('adds a track when toggled', () => {
    const { selectedTracks, toggleTrackSelection } = useTidal()
    const track = { id: '1', title: 'Track 1' } // Added title for clarity, though only id is used in current logic
    toggleTrackSelection(track)
    expect(selectedTracks.value).toHaveLength(1)
    expect(selectedTracks.value[0]).toStrictEqual(track)
  })

  it('removes a track when toggled twice', () => {
    const { selectedTracks, toggleTrackSelection } = useTidal()
    const track = { id: '1', title: 'Track 1' }
    toggleTrackSelection(track) // Add
    toggleTrackSelection(track) // Remove
    expect(selectedTracks.value).toHaveLength(0)
  })

  it('limits selection to 10 tracks', () => {
    const { selectedTracks, toggleTrackSelection } = useTidal()
    for (let i = 0; i < 12; i++) {
      toggleTrackSelection({ id: String(i), title: `Track ${i}` })
    }
    expect(selectedTracks.value).toHaveLength(10)
  })

  it('does not add the 11th track', () => {
    const { selectedTracks, toggleTrackSelection } = useTidal()
    for (let i = 0; i < 10; i++) {
      toggleTrackSelection({ id: String(i), title: `Track ${i}` })
    }
    const eleventhTrack = { id: '10', title: 'Track 10' }
    toggleTrackSelection(eleventhTrack) // Attempt to add 11th track
    expect(selectedTracks.value).toHaveLength(10)
    // Ensure the 11th track was not added
    expect(selectedTracks.value.find(t => t.id === '10')).toBeUndefined()
  })

  it('allows removing a track when at the limit and then adding a new one', () => {
    const { selectedTracks, toggleTrackSelection } = useTidal()
    // Fill to the limit
    for (let i = 0; i < 10; i++) {
      toggleTrackSelection({ id: String(i), title: `Track ${i}` })
    }
    expect(selectedTracks.value).toHaveLength(10)

    // Remove one track
    const trackToRemove = selectedTracks.value[0]
    toggleTrackSelection(trackToRemove)
    expect(selectedTracks.value).toHaveLength(9)
    expect(selectedTracks.value.find(t => t.id === trackToRemove.id)).toBeUndefined()

    // Add a new track
    const newTrack = { id: '100', title: 'New Track 100' }
    toggleTrackSelection(newTrack)
    expect(selectedTracks.value).toHaveLength(10)
    expect(selectedTracks.value.find(t => t.id === newTrack.id)).toBeDefined()
  })
})
