# Copyright (c) 2023, Aakvatech and contributors
# For license information, please see license.txt

import frappe


def get_xml(doc):
    xml = get_first_xml_part(doc)
    xml += get_payments_xml_part(doc)
    xml += get_last_xml_part(doc)
    return xml


def get_first_xml_part(doc):
    settings_doc = frappe.get_cached_doc("Stanbic Setting", doc.stanbic_setting)
    part = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">
	<CstmrCdtTrfInitn>
		<GrpHdr>
		<MsgId>{doc.name}</MsgId>
		<CreDtTm>{doc.modified}</CreDtTm>
		<Authstn>
			<Cd>AUTH</Cd>
		</Authstn>
		<NbOfTxs>{doc.number_of_transactions}</NbOfTxs>
		<CtrlSum>{doc.control_sum}</CtrlSum>
		<InitgPty>
			<Nm>{settings_doc.payment_type}</Nm>
			<Id>
				<OrgId>
					<Othr>
					<Id>{settings_doc.customerid}</Id>
						<SchmeNm>
							<Prtry>{settings_doc.initiating_party_name}</Prtry>
						</SchmeNm>
					</Othr>
				</OrgId>
			</Id>
		</InitgPty>
		</GrpHdr>
		<PmtInf>
			<PmtInfId>{doc.name}</PmtInfId>
				<PmtMtd>TRF</PmtMtd>
				<BtchBookg>false</BtchBookg>
				<NbOfTxs>1</NbOfTxs>
				<CtrlSum>20.00</CtrlSum>
			<PmtTpInf>
				<InstrPrty>HIGH</InstrPrty>
			</PmtTpInf>
			<ReqdExctnDt>2014-07-23</ReqdExctnDt>
			<Dbtr>
				<Nm>ORDERING CUSTOMER NAME</Nm>
			</Dbtr>
			<DbtrAcct>
				<Id>
					<Othr>
						<Id>22006622</Id>
					</Othr>
				</Id>
				<Ccy>ZAR</Ccy>
			</DbtrAcct>
			<DbtrAgt>
				<FinInstnId>
					<ClrSysMmbId>
						<MmbId>020909</MmbId>
					</ClrSysMmbId>
					<Nm>StandardBankZ.A</Nm>
					<PstlAdr>
						<Ctry>ZA</Ctry>
					</PstlAdr>
				</FinInstnId>
			</DbtrAgt>
    """
    return part


def get_payment_part(payment):
    part = """
			<CdtTrfTxInf>
				<PmtId>
					<InstrId>5574152</InstrId>
					<EndToEndId>5574152</EndToEndId>
				</PmtId>
				<Amt>
					<InstdAmt Ccy="ZAR">20.00</InstdAmt>
				</Amt>
				<CdtrAgt>
					<FinInstnId>
						<ClrSysMmbId>
							<MmbId>654321</MmbId>
						</ClrSysMmbId>
						<PstlAdr>
							<Ctry>ZA</Ctry>
						</PstlAdr>
					</FinInstnId>
				</CdtrAgt>
				<Cdtr>
					<Nm>BENEFICIARY NAME</Nm>
					<PstlAdr>
						<Ctry>ZA</Ctry>
					</PstlAdr>
				</Cdtr>
				<CdtrAcct>
					<Id>
					<Othr>
						<Id>151113087</Id>
					</Othr>
					</Id>
				</CdtrAcct>
				<RmtInf>
					<Ustrd>BENEFICIARY STATEMENT REF</Ustrd>
				</RmtInf>
			</CdtTrfTxInf>
    """

    return part


def get_payments_xml_part(doc):
    parts = ""

    for payment in doc.stanbic_payments_info:
        parts += get_payment_part(payment)

    return parts


def get_last_xml_part(doc):
    part = """
	</PmtInf>
	</CstmrCdtTrfInitn>
</Document>
    """
    return part
