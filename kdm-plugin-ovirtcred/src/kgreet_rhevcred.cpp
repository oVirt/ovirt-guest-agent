
#include "kgreet_rhevcred.h"
#include "RhevCred.h"

#include <kglobal.h>
#include <klocale.h>

#include <QtGui/QLayout>
#include <QtGui/QLabel>

#define KDM_RHEVCRED_SERVER_DBUS_NAME      "com.redhat.rhevm.Credentials"
#define KDM_RHEVCRED_SERVER_DBUS_PATH      "/com/redhat/rhevm/Credentials"
#define KDM_RHEVCRED_SERVER_DBUS_INTERFACE KDM_RHEVCRED_SERVER_DBUS_NAME

KRhevCredGreeter::KRhevCredGreeter(KGreeterPluginHandler *handler,
                                   QWidget *parent,
                                   const QString &fixedEntity,
                                   Function func, Context ctx) :
    QObject(),
    KGreeterPlugin(handler)
{
    Q_UNUSED(parent);
    Q_UNUSED(fixedEntity);
    Q_UNUSED(func);
    Q_UNUSED(ctx);

    parent = new QWidget(parent);
    parent->setObjectName("talker");
    widgetList << parent;

    QBoxLayout *grid = new QBoxLayout(QBoxLayout::LeftToRight, parent);
    m_titleLabel = new QLabel(i18n("RHEV-M Automatic Login System"), parent);
    grid->addWidget(m_titleLabel, 0, Qt::AlignHCenter);    

    m_Credentials = new RhevCred(KDM_RHEVCRED_SERVER_DBUS_NAME, KDM_RHEVCRED_SERVER_DBUS_PATH,
        QDBusConnection::systemBus(), 0);
        
    QObject::connect(m_Credentials, SIGNAL(UserAuthenticated(QString)),
        this, SLOT(userAuthenticated(QString)));
}

KRhevCredGreeter::~KRhevCredGreeter()
{
    abort();
    qDeleteAll(widgetList);

    delete m_Credentials;
}

void KRhevCredGreeter::loadUsers(const QStringList &users)
{
    // We do no offer a selectable users list.
    Q_UNUSED(users);
}

void KRhevCredGreeter::presetEntity(const QString &entity, int field)
{
    // We do not care about preloaded users either.
    Q_UNUSED(entity);
    Q_UNUSED(field);
}

QString KRhevCredGreeter::getEntity() const
{
    return QString();
}

void KRhevCredGreeter::setUser(const QString &user)
{
    Q_UNUSED(user);
}

void KRhevCredGreeter::setEnabled(bool on)
{
    Q_UNUSED(on);
}

bool KRhevCredGreeter::textMessage(const char *message, bool error)
{
    if (error) {
        // Stop authentication.
        abort();
    } else {
        handler->gplugMsgBox(QMessageBox::Information, message);
    }

    return true;
}

void KRhevCredGreeter::textPrompt(const char *prompt, bool echo, bool nonBlocking)
{
    Q_UNUSED(echo);
    Q_UNUSED(nonBlocking);
    
    QString text = QString(prompt);
    if (text.contains(QString("Token?"), Qt::CaseInsensitive)) {
        handler->gplugReturnText(m_token.toAscii(), KGreeterPluginHandler::IsSecret);
        m_token.clear();
    } else {
        abort();
    }
}

bool KRhevCredGreeter::binaryPrompt(const char *prompt, bool nonBlocking)
{
    Q_UNUSED(prompt);
    Q_UNUSED(nonBlocking);
    return true;
}

void KRhevCredGreeter::start()
{

}

void KRhevCredGreeter::suspend()
{

}

void KRhevCredGreeter::resume()
{

}

void KRhevCredGreeter::next()
{

}

void KRhevCredGreeter::abort()
{

}

void KRhevCredGreeter::succeeded()
{

}

void KRhevCredGreeter::failed()
{

}

void KRhevCredGreeter::revive()
{

}

void KRhevCredGreeter::clear()
{

}

void KRhevCredGreeter::userAuthenticated(QString token)
{
    m_token = token;
    
    handler->gplugStart();
}

static bool init(const QString &,
                 QVariant (*getConf)(void *, const char *, const QVariant &),
                 void *ctx)
{
    Q_UNUSED(getConf);
    Q_UNUSED(ctx);
    KGlobal::locale()->insertCatalog("kgreet_rhevcred");
    return true;
}

static void done()
{
    KGlobal::locale()->removeCatalog("kgreet_rhevcred");
}

static KGreeterPlugin* create(KGreeterPluginHandler *handler,
                              QWidget *parent,
                              const QString &fixedEntity,
                              KGreeterPlugin::Function func,
                              KGreeterPlugin::Context ctx)
{
    return new KRhevCredGreeter(handler, parent, fixedEntity, func, ctx);
}

KDE_EXPORT KGreeterPluginInfo kgreeterplugin_info = {
    I18N_NOOP2("@item:inmenu authentication method", "RHEV-M Authentication"), "rhevcred",
    KGreeterPluginInfo::Local | KGreeterPluginInfo::Presettable,
    init, done, create
};

#include "kgreet_rhevcred.moc"
