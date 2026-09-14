import asyncio
from aiosmtpd.controller import Controller

class DebugHandler:
    async def handle_DATA(self, server, session, envelope):
        print('─' * 70)
        print('Mail from:', envelope.mail_from)
        print('Mail to  :', envelope.rcpt_tos)
        print('Data     :\n', envelope.content.decode('utf8', errors='replace'))
        print('─' * 70)
        return '250 Message accepted'

if __name__ == '__main__':
    controller = Controller(DebugHandler(), hostname='localhost', port=8025)
    controller.start()
    print('Debug SMTP server running on localhost:8025')
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
