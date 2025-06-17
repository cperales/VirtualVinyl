import { useSpotify } from '../src/composables/useSpotify.js'

describe('useSpotify', () => {
  beforeEach(() => {
    const { selectedTracks } = useSpotify()
    selectedTracks.value = []
  })

  it('adds a track when toggled', () => {
    const { selectedTracks, toggleTrackSelection } = useSpotify()
    const track = { id: '1' }
    toggleTrackSelection(track)
    expect(selectedTracks.value).toHaveLength(1)
    expect(selectedTracks.value[0]).toStrictEqual(track)
  })

  it('removes a track when toggled twice', () => {
    const { selectedTracks, toggleTrackSelection } = useSpotify()
    const track = { id: '1' }
    toggleTrackSelection(track)
    toggleTrackSelection(track)
    expect(selectedTracks.value).toHaveLength(0)
  })

  it('limits selection to 10 tracks', () => {
    const { selectedTracks, toggleTrackSelection } = useSpotify()
    for (let i = 0; i < 12; i++) {
      toggleTrackSelection({ id: String(i) })
    }
    expect(selectedTracks.value).toHaveLength(10)
  })
})
