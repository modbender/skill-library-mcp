const nodemailer = require('nodemailer');

class SmtpClient {
  constructor(config) {
    this.config = config;
    this.transporter = null;
  }

  async connect() {
    this.transporter = nodemailer.createTransport(this.config);
    await this.transporter.verify();
  }

  async sendMail(options) {
    if (!this.transporter) {
      await this.connect();
    }

    const mailOptions = {
      from: this.config.auth.user,
      ...options
    };

    return this.transporter.sendMail(mailOptions);
  }

  async sendSimple(to, subject, body, options = {}) {
    return this.sendMail({
      to,
      subject,
      text: body,
      ...options
    });
  }

  async sendHtml(to, subject, html, options = {}) {
    return this.sendMail({
      to,
      subject,
      html,
      ...options
    });
  }

  async reply(originalMessage, body, options = {}) {
    const replySubject = originalMessage.subject.startsWith('Re:') 
      ? originalMessage.subject 
      : `Re: ${originalMessage.subject}`;

    return this.sendMail({
      to: originalMessage.from,
      subject: replySubject,
      text: body,
      inReplyTo: originalMessage.messageId,
      references: originalMessage.references || originalMessage.messageId,
      ...options
    });
  }
}

module.exports = SmtpClient;
