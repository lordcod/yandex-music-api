
import string
from typing import List, Literal, Self, TypeVar, TypedDict, Union


InvocationInfoPayload = TypedDict("InvocationInfoPayload", {
    "exec-duration-millis": int,
    "hostname": str,
    "req-id": str,
    "app-name": int
})
T = TypeVar('T')
VisibilityType = Literal["public", "private"]
SearchType = Literal['artist', 'album', 'track', 'podcast', 'all']


class PagerPayload(TypedDict):
    page: int
    perPage: int
    total: int


class CoverPayload(TypedDict):
    custom: bool
    dir: str
    type: Literal['pic']
    itemsUri: List[str]
    uri: str
    version: str
    error: str


class OwnerPayload(TypedDict):
    login: str
    name: str
    sex: str
    uid: int
    verified: bool


class PlaylistTagPayload(TypedDict):
    id: str
    value: str


class TrackMajorPayload(TypedDict):
    id: int
    name: str


class TrackNormalizationPayload(TypedDict):
    gain: int
    peak: int


class ArtistPayload(TypedDict):
    composer: bool
    cover: CoverPayload
    decomposed: List[dict]
    genres: List[dict]
    id: str
    name: str
    various: bool
    popularTracks: List['TrackPayload']
    ticketsAvailable: bool
    regions: List[str]


class LabelPayload(TypedDict):
    id: int
    name: str


class AlbumPayload(TypedDict):
    id: int
    error: str
    title: str
    type: Literal['single', 'podcast']
    metaType: Literal['single', 'podcast', 'music']
    year: int
    releaseDate: str
    coverUri: str
    ogImage: str
    genre: str
    buy: List[dict]
    trackCount: int
    recent: bool
    veryImportant: bool
    artists: List[ArtistPayload]
    labels: List[LabelPayload]
    available: bool
    availableForPremiumUsers: bool
    availableForMobile: bool
    availablePartially: bool
    bests: List[int]
    prerolls: List[dict]
    volumes: List[List['TrackPayload']]


class TrackShortPayload(TypedDict):
    id: int
    albumId: int
    timestamp: str


class TrackListPayload(TypedDict):
    uid: int
    revision: int
    tracks: TrackShortPayload


class TrackPayload(TypedDict):
    albums: List[AlbumPayload]
    artists: List[ArtistPayload]
    available: bool
    availableForPremiumUsers: bool
    availableFullWithoutPermission: bool
    coverUri: str
    durationMs: int
    fileSize: int
    id: str
    lyricsAvailable: bool
    major: TrackMajorPayload
    normalization: TrackNormalizationPayload
    ogImage: str
    previewDurationMs: int
    realId: str
    rememberPosition: bool
    storageDir: str
    title: str
    type: str


class TrackItemPayload(TypedDict):
    id: int
    playCount: int
    recent: bool
    timestamp: str
    tracks: List[TrackPayload]


class TrackDownloadinfoPayload(TypedDict):
    codec: Literal['mp3', 'aac']
    gain: bool
    preview: string
    downloadInfoUrl: str
    direct: bool
    bitrateInKbps: int


class PlaylistPayload(TypedDict):
    playlistUuid: str
    description: str
    descriptionFormatted: str
    available: bool
    collective: bool
    cover: CoverPayload
    created: str
    modified: str
    backgroundColor: str
    textColor: str
    durationMs: int
    isBanner: bool
    isPremiere: bool
    kind: int
    ogImage: str
    owner: OwnerPayload
    prerolls: List[dict]
    revision: int
    snapshot: int
    tags: List[PlaylistTagPayload]
    title: str
    trackCount: int
    uid: int
    visibility: VisibilityType
    likesCount: int
    tracks: List[TrackItemPayload]


class PlaylistRecommendationsPayload(TypedDict):
    batch_id: str
    track: TrackPayload


class LibraryPlaylistPayload(TypedDict):
    library: TrackListPayload


class LyricsPayload(TypedDict):
    id: int
    lyrics: str
    hasRights: bool
    fullLyrics: str
    textLanguage: str
    showTranslation: str
    url: str


class VideoSupplementPayload(TypedDict):
    cover: str
    provider: str
    title: str
    providerVideoId: str
    url: str
    embedUrl: str
    embed: str


class SupplementPayload(TypedDict):
    id: int
    lyrics: LyricsPayload
    videos: VideoSupplementPayload
    radioIsAvailable: bool
    description: str


class SimilarTracksPayload(TypedDict):
    track: TrackPayload
    similarTracks: List[TrackPayload]


class ArtistWithTrackPayload(TypedDict):
    artist: ArtistPayload
    tracks: List[List[str]]


class TrackCoverPayload(TypedDict):
    {
        "type": "from-album-cover",
        "uri": "avatars.yandex.net/get-music-content/2811629/241e33d2.a.12664250-1/%%",
        "prefix": "241e33d2.a.12664250-1"
    }


class BandlinkScannerPayload(TypedDict):
    title: str
    subtitle: str
    url: str
    imgUrl: str


class ArtistStatsPayload(TypedDict):
    lastMonthListeners: int
    lastMonthListenersDelta: int


class CustomWavePayload(TypedDict):
    title: str
    animationUrl: str
    header: str
    backgroundImageUrl: str


class PlaylistShortPayload(TypedDict):
    uid: int
    kind: int


class ArtistBriefInfoPayload(TypedDict):
    artist: ArtistPayload
    albums: List[AlbumPayload]
    alsoAlbums: List[AlbumPayload]
    lastReleaseIds: List[int]
    popularTracks: List[TrackPayload]
    bandlinkScannerLink: BandlinkScannerPayload
    similarArtists: List[ArtistPayload]
    allCovers: List[TrackCoverPayload]
    concerts: List[str]
    videos: list
    clips: list
    vinyls: list
    hasPromotions: bool
    lastReleases: List[TrackPayload]
    extraActions: list
    stats: ArtistStatsPayload
    customWave: CustomWavePayload
    playlistIds: List[PlaylistShortPayload]
    playlists: List[PlaylistPayload]
    hasTrailer: bool


class ArtistWithTracksPayload(TypedDict):
    pager: PagerPayload
    tracks: List[TrackPayload]


class ArtistWithAlbumsPayload(TypedDict):
    pager: PagerPayload
    albums: List[AlbumPayload]


class VideoPayload(TypedDict):
    pass


class BestPayload(TypedDict):
    type: str
    text: str
    result: Union[TrackPayload, ArtistPayload, AlbumPayload,
                  PlaylistPayload, VideoPayload]


class SearchResultPayload(TypedDict):
    type: str
    total: int
    perPage: int
    order: int
    results: List[T]

    def __class_getitem__(cls, type_object: T):
        return cls


class SearchPayload(TypedDict):
    searchResultId: str
    text: str
    best: BestPayload
    albums: SearchResultPayload[AlbumPayload]
    artists: SearchResultPayload[ArtistPayload]
    playlists: SearchResultPayload[PlaylistPayload]
    tracks: SearchResultPayload[TrackPayload]
    videos: SearchResultPayload[VideoPayload]
    podcast: SearchResultPayload
    podcast_episodes: SearchResultPayload
    page: int
    perPage: int
    misspellCorrected: str
    misspellOriginal: str
    nocorrect: bool
