import datetime
from enum import Enum
from typing import Optional
from .. import db

class AuditAction(Enum):
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"

    @staticmethod
    def from_string(string) -> Optional["AuditAction"]:
        return {
            AuditAction.INSERT.value: AuditAction.INSERT,
            AuditAction.UPDATE.value: AuditAction.UPDATE,
            AuditAction.DELETE.value: AuditAction.DELETE,
            }[string]

    def __str__(self) -> str:
        return self.value

def audit_listener(session, flush_context, get_jwt_identity, socketio):
    try:
        id = get_jwt_identity() if get_jwt_identity != None else None
    except:
        id = None

    for obj in session.new:
        create_audit_entry(session, obj, action=AuditAction.INSERT, issuer_id=id)
    for obj in session.dirty:
        create_audit_entry(session, obj, action=AuditAction.UPDATE, issuer_id=id)
    for obj in session.deleted:
        create_audit_entry(session, obj, action=AuditAction.DELETE, issuer_id=id)
    
    if socketio != None:
        socketio.emit("data",{"last_data_change": datetime.datetime.now().isoformat(),})

def create_audit_entry(session, instance, action:AuditAction, issuer_id:Optional["int"]):
    """
    Erstellt einen Audit-Eintrag für das übergebene Objekt.
    """
    audit_table_name = f"{instance.__tablename__}_audit"
    audit_table = db.metadata.tables.get(audit_table_name)
    if audit_table == None:
        return  # Keine Audit-Tabelle definiert
    
    # Audit-Daten vorbereiten
    audit_data = {col.name: getattr(instance, col.name) for col in instance.__table__.columns} if instance != None else {}
    audit_data.update({
        "audit_id": None,
        "audit_action": action,
        "audit_datetime": datetime.datetime.now(),
        "audit_issuer_id": issuer_id
    })
    if audit_table.name == "employees" + "_audit":
        audit_data.update({
            "password": "***"
        })
    
    # Audit-Eintrag hinzufügen
    session.execute(audit_table.insert().values(**audit_data))