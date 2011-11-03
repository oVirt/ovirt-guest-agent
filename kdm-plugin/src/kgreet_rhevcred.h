
#ifndef KGREET_RHEVCRED_H
#define KGREET_RHEVCRED_H

#include <kgreeterplugin.h>

#include <QtCore/QObject>

class RhevCred;

class KRhevCredGreeter : public QObject, public KGreeterPlugin
{
    Q_OBJECT

public:
    KRhevCredGreeter(KGreeterPluginHandler *handler,
        QWidget *parent,
        const QString &fixedEntitiy,
        Function func, Context ctx );
    virtual ~KRhevCredGreeter();

        // KGreeterPlugin's methods.

    virtual void loadUsers(const QStringList &users);
    virtual void presetEntity(const QString &entity, int field);
    virtual QString getEntity() const;
    virtual void setUser(const QString &user);
    virtual void setEnabled(bool on);
    virtual bool textMessage(const char *message, bool error);
    virtual void textPrompt(const char *prompt, bool echo, bool nonBlocking);
    virtual bool binaryPrompt(const char *prompt, bool nonBlocking);
    virtual void start();
    virtual void suspend();
    virtual void resume();
    virtual void next();
    virtual void abort();
    virtual void succeeded();
    virtual void failed();
    virtual void revive();
    virtual void clear();

public Q_SLOTS:
    void userAuthenticated(QString token);

private:
    RhevCred *m_Credentials;
    QLabel *m_titleLabel;
    QString m_token;
};

#endif // KGREET_RHEVCRED_H
