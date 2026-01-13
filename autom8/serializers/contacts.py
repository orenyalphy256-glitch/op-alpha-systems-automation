# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""
Contact Resource Serializers
"""


def serialize_contact(contact):
    """Serialize a Contact model instance."""
    if not contact:
        return None

    return {
        "id": contact.id,
        "name": contact.name,
        "phone": contact.phone,
        "email": contact.email,  # Always present in response, may be None
        "created_at": contact.created_at.isoformat() if contact.created_at else None,
        "updated_at": contact.updated_at.isoformat() if contact.updated_at else None,
    }


def serialize_contacts_page(contacts, total, offset, limit):
    """Serialize paginated contacts list with metadata."""
    return {
        "contacts": [serialize_contact(c) for c in contacts],
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    }


# Module exports
__all__ = [
    "serialize_contact",
    "serialize_contacts_page",
]
