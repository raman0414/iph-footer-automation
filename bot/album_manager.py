import asyncio


class AlbumManager:
    """
    Collects photos that belong to the same Telegram media group (album).

    Telegram sends album photos one-by-one, so we wait a short time
    before assuming the album is complete.
    """

    albums = {}
    timers = {}

    WAIT_TIME = 2.0

    @classmethod
    async def add_photo(
        cls,
        media_group_id,
        photo_info,
        callback
    ):

        # Create album if it doesn't exist
        if media_group_id not in cls.albums:
            cls.albums[media_group_id] = []

        # Store photo information
        cls.albums[media_group_id].append(photo_info)

        # Cancel previous timer
        if media_group_id in cls.timers:
            cls.timers[media_group_id].cancel()

        # Start a new timer
        cls.timers[media_group_id] = asyncio.create_task(
            cls._wait_for_completion(
                media_group_id,
                callback
            )
        )

    @classmethod
    async def _wait_for_completion(
        cls,
        media_group_id,
        callback
    ):

        try:

            # Wait for more photos
            await asyncio.sleep(cls.WAIT_TIME)

            photos = cls.albums.pop(
                media_group_id,
                []
            )

            cls.timers.pop(
                media_group_id,
                None
            )

            if photos:
                await callback(photos)

        except asyncio.CancelledError:
            # Timer restarted because another photo arrived.
            pass

    @classmethod
    def is_album(cls, update):

        return update.message.media_group_id is not None

    @classmethod
    def get_album_id(cls, update):

        return update.message.media_group_id