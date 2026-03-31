"""XARF v4 Copyright category type definitions.

Mirrors ``types-copyright.ts`` from the JavaScript reference implementation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from xarf.models import XARFReport


class CopyrightBaseReport(XARFReport):
    """Shared fields for all copyright-category reports.

    Attributes:
        category: Always ``"copyright"`` for this category.
        rights_holder: Name of the rights holder filing the report.
        work_category: Category of the copyrighted work (e.g. ``"music"``, ``"film"``).
        work_title: Title of the copyrighted work.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    category: Literal["copyright"]
    rights_holder: str | None = None
    work_category: str | None = None
    work_title: str | None = None


class CopyrightCopyrightReport(CopyrightBaseReport):
    """Copyright - Direct Infringement / DMCA report.

    Attributes:
        type: Always ``"copyright"``.
        infringing_url: URL where infringing content is hosted (required).
        infringement_type: Type of infringement (e.g. ``"reproduction"``,
            ``"distribution"``).
        original_url: URL of the original legitimate work.
    """

    type: Literal["copyright"]
    infringing_url: str
    infringement_type: str | None = None
    original_url: str | None = None


class SwarmInfo(BaseModel):
    """BitTorrent swarm information.

    Note: either ``info_hash`` or ``magnet_uri`` is required at runtime (enforced
    by AJV/jsonschema validation, not by Pydantic).

    Attributes:
        info_hash: Hex-encoded info hash of the torrent.
        magnet_uri: Magnet URI for the torrent.
        torrent_name: Display name of the torrent.
        file_count: Number of files in the torrent.
        total_size: Total size of the torrent in bytes.
    """

    model_config = ConfigDict(populate_by_name=True)

    info_hash: str | None = None
    magnet_uri: str | None = None
    torrent_name: str | None = None
    file_count: int | None = None
    total_size: int | None = None


class PeerInfo(BaseModel):
    """BitTorrent peer information.

    Attributes:
        peer_id: Peer ID observed in the swarm.
        client_version: BitTorrent client version string.
        upload_amount: Amount of data uploaded by this peer in bytes.
        download_amount: Amount of data downloaded by this peer in bytes.
    """

    model_config = ConfigDict(populate_by_name=True)

    peer_id: str | None = None
    client_version: str | None = None
    upload_amount: int | None = None
    download_amount: int | None = None


class CopyrightP2pReport(CopyrightBaseReport):
    """Copyright - P2P (BitTorrent / peer-to-peer) report.

    Attributes:
        type: Always ``"p2p"``.
        p2p_protocol: P2P protocol used (required, e.g. ``"bittorrent"``).
        swarm_info: Information about the torrent swarm (required).
        detection_method: How the infringement was detected.
        peer_info: Information about the infringing peer.
        release_date: ISO 8601 release date of the work.
    """

    type: Literal["p2p"]
    p2p_protocol: str
    swarm_info: SwarmInfo
    detection_method: str | None = None
    peer_info: PeerInfo | None = None
    release_date: str | None = None


class FileInfo(BaseModel):
    """Cyberlocker file metadata.

    Attributes:
        filename: Original filename of the infringing file.
        file_size: File size in bytes.
        file_hash: Hash of the file (algorithm implied by context).
        upload_date: ISO 8601 date the file was uploaded.
        download_count: Number of times the file has been downloaded.
    """

    model_config = ConfigDict(populate_by_name=True)

    filename: str | None = None
    file_size: int | None = None
    file_hash: str | None = None
    upload_date: str | None = None
    download_count: int | None = None


class CyberlockerTakedownInfo(BaseModel):
    """Information about previous takedown requests for cyberlocker content.

    Attributes:
        previous_requests: Number of prior takedown requests submitted.
        service_response_time: Typical response time of the service.
        automated_removal: Whether the service offers automated removal.
    """

    model_config = ConfigDict(populate_by_name=True)

    previous_requests: int | None = None
    service_response_time: str | None = None
    automated_removal: bool | None = None


class CyberlockerUploaderInfo(BaseModel):
    """Information about the uploader on a cyberlocker service.

    Attributes:
        username: Username of the uploader.
        user_id: Platform-specific user identifier.
        account_type: Account tier of the uploader.
    """

    model_config = ConfigDict(populate_by_name=True)

    username: str | None = None
    user_id: str | None = None
    account_type: Literal["free", "premium", "business", "unknown"] | None = None


class CopyrightCyberlockerReport(CopyrightBaseReport):
    """Copyright - Cyberlocker report.

    Attributes:
        type: Always ``"cyberlocker"``.
        hosting_service: Name of the cyberlocker service (required).
        infringing_url: Direct URL to the infringing file (required).
        access_method: How the file is accessed (e.g. ``"direct_link"``).
        file_info: Metadata about the infringing file.
        takedown_info: Information about previous takedown requests.
        uploader_info: Information about the uploader.
    """

    type: Literal["cyberlocker"]
    hosting_service: str
    infringing_url: str
    access_method: str | None = None
    file_info: FileInfo | None = None
    takedown_info: CyberlockerTakedownInfo | None = None
    uploader_info: CyberlockerUploaderInfo | None = None


class UgcContentInfo(BaseModel):
    """Content information for a UGC platform upload.

    Attributes:
        content_id: Platform-specific content identifier.
        content_title: Title of the uploaded content.
        content_description: Description of the uploaded content.
        upload_date: ISO 8601 date the content was uploaded.
        content_duration: Duration of the content in seconds.
        view_count: Number of views.
        like_count: Number of likes.
    """

    model_config = ConfigDict(populate_by_name=True)

    content_id: str | None = None
    content_title: str | None = None
    content_description: str | None = None
    upload_date: str | None = None
    content_duration: int | None = None
    view_count: int | None = None
    like_count: int | None = None


class UgcUploaderInfo(BaseModel):
    """Uploader information for a UGC platform.

    Attributes:
        username: Username of the uploader.
        user_id: Platform-specific user identifier.
        account_verified: Whether the account is verified.
        subscriber_count: Number of subscribers/followers.
        account_creation_date: ISO 8601 date the account was created.
    """

    model_config = ConfigDict(populate_by_name=True)

    username: str | None = None
    user_id: str | None = None
    account_verified: bool | None = None
    subscriber_count: int | None = None
    account_creation_date: str | None = None


class UgcMatchDetails(BaseModel):
    """Content match details from a reference fingerprinting system.

    Attributes:
        match_confidence: Confidence of the content match (0–1).
        match_duration: Duration of the matched segment in seconds.
        match_percentage: Percentage of the work matched (0–100).
        reference_id: Reference system identifier for the matched work.
    """

    model_config = ConfigDict(populate_by_name=True)

    match_confidence: float | None = None
    match_duration: float | None = None
    match_percentage: float | None = None
    reference_id: str | None = None


class UgcMonetizationInfo(BaseModel):
    """Monetization information for UGC platform content.

    Attributes:
        monetized: Whether the content is monetized.
        ad_revenue: Whether the content generates ad revenue.
        premium_content: Whether the content is behind a paywall.
    """

    model_config = ConfigDict(populate_by_name=True)

    monetized: bool | None = None
    ad_revenue: bool | None = None
    premium_content: bool | None = None


class CopyrightUgcPlatformReport(CopyrightBaseReport):
    """Copyright - UGC Platform report.

    Attributes:
        type: Always ``"ugc_platform"``.
        infringing_url: URL of the infringing content (required).
        platform_name: Name of the UGC platform (required).
        content_info: Metadata about the infringing content.
        infringement_type: Type of infringement (e.g. ``"full_copy"``).
        match_details: Content match details from a fingerprinting system.
        monetization_info: Monetization information.
        uploader_info: Information about the uploader.
    """

    type: Literal["ugc_platform"]
    infringing_url: str
    platform_name: str
    content_info: UgcContentInfo | None = None
    infringement_type: str | None = None
    match_details: UgcMatchDetails | None = None
    monetization_info: UgcMonetizationInfo | None = None
    uploader_info: UgcUploaderInfo | None = None


class LinkSiteLinkInfo(BaseModel):
    """Link metadata from a link site listing.

    Attributes:
        page_title: Title of the link site page.
        posting_date: ISO 8601 date the link was posted.
        uploader: Username of who posted the link.
        download_count: Reported download count for the link.
        link_count: Number of links on the page.
        comments_count: Number of comments on the page.
    """

    model_config = ConfigDict(populate_by_name=True)

    page_title: str | None = None
    posting_date: str | None = None
    uploader: str | None = None
    download_count: int | None = None
    link_count: int | None = None
    comments_count: int | None = None


class LinkedContentItem(BaseModel):
    """A single linked content item on a link site.

    Attributes:
        target_url: URL the link points to (required).
        link_type: Type of link (required).
        hosting_service: Name of the hosting service at ``target_url``.
        file_size: File size in bytes, if known.
    """

    model_config = ConfigDict(populate_by_name=True)

    target_url: str
    link_type: Literal[
        "torrent_file",
        "magnet_link",
        "direct_download",
        "streaming_link",
        "usenet_nzb",
        "other",
    ]
    hosting_service: str | None = None
    file_size: int | None = None


class LinkSiteRanking(BaseModel):
    """Ranking information for a link site.

    Attributes:
        alexa_rank: Alexa traffic rank of the site.
        popularity_score: Relative popularity score.
    """

    model_config = ConfigDict(populate_by_name=True)

    alexa_rank: int | None = None
    popularity_score: float | None = None


class CopyrightLinkSiteReport(CopyrightBaseReport):
    """Copyright - Link Site report.

    Attributes:
        type: Always ``"link_site"``.
        infringing_url: URL of the link site page listing infringing links (required).
        site_name: Name of the link site (required).
        link_info: Metadata about the link listing.
        linked_content: Individual links to infringing content.
        search_terms: Search terms used to find the listing.
        site_category: Category of the link site (e.g. ``"warez"``, ``"general"``).
        site_ranking: Traffic ranking information for the site.
    """

    type: Literal["link_site"]
    infringing_url: str
    site_name: str
    link_info: LinkSiteLinkInfo | None = None
    linked_content: list[LinkedContentItem] | None = None
    search_terms: list[str] | None = None
    site_category: str | None = None
    site_ranking: LinkSiteRanking | None = None


class MessageInfo(BaseModel):
    """Usenet message metadata.

    Attributes:
        message_id: Message-ID header of the Usenet article (required).
        subject: Subject of the Usenet article.
        from_header: From header of the Usenet article.
        posting_date: ISO 8601 date the article was posted.
        part_number: Part number for multi-part posts.
        total_parts: Total number of parts in a multi-part post.
        file_size: File size in bytes.
    """

    model_config = ConfigDict(populate_by_name=True)

    message_id: str
    subject: str | None = None
    from_header: str | None = None
    posting_date: str | None = None
    part_number: int | None = None
    total_parts: int | None = None
    file_size: int | None = None


class UsenetEncodingInfo(BaseModel):
    """Encoding information for Usenet content.

    Attributes:
        encoding_format: Encoding format used (e.g. ``"yenc"``).
        par2_recovery: Whether PAR2 recovery files are present.
        rar_compression: Whether RAR compression was used.
    """

    model_config = ConfigDict(populate_by_name=True)

    encoding_format: Literal["yenc", "uuencode", "base64", "other"] | None = None
    par2_recovery: bool | None = None
    rar_compression: bool | None = None


class UsenetNzbInfo(BaseModel):
    """NZB file metadata for Usenet content.

    Attributes:
        nzb_name: Name of the NZB file.
        nzb_url: URL where the NZB file can be found.
        indexer_site: Usenet indexer site that published the NZB.
        completion_percentage: Download completion percentage (0–100).
    """

    model_config = ConfigDict(populate_by_name=True)

    nzb_name: str | None = None
    nzb_url: str | None = None
    indexer_site: str | None = None
    completion_percentage: float | None = None


class UsenetServerInfo(BaseModel):
    """Usenet server information.

    Attributes:
        nntp_server: Hostname of the NNTP server.
        server_group: Newsgroup name on the server.
        retention_days: Number of days articles are retained.
    """

    model_config = ConfigDict(populate_by_name=True)

    nntp_server: str | None = None
    server_group: str | None = None
    retention_days: int | None = None


class CopyrightUsenetReport(CopyrightBaseReport):
    """Copyright - Usenet report.

    Attributes:
        type: Always ``"usenet"``.
        newsgroup: Usenet newsgroup where the content was posted (required).
        message_info: Usenet article metadata (required).
        detection_method: How the infringement was detected.
        encoding_info: Encoding information for the content.
        nzb_info: NZB file metadata.
        server_info: Usenet server information.
    """

    type: Literal["usenet"]
    newsgroup: str
    message_info: MessageInfo
    detection_method: str | None = None
    encoding_info: UsenetEncodingInfo | None = None
    nzb_info: UsenetNzbInfo | None = None
    server_info: UsenetServerInfo | None = None


# Category-level union alias (for isinstance checks and type annotations).
CopyrightReport = (
    CopyrightCopyrightReport
    | CopyrightP2pReport
    | CopyrightCyberlockerReport
    | CopyrightUgcPlatformReport
    | CopyrightLinkSiteReport
    | CopyrightUsenetReport
)
"""Union of all copyright-category report types."""
